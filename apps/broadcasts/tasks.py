import logging
import requests

from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from apps.broadcasts.models import Message, Broadcast
from apps.clients.models import Client
from core.settings import PROBE_URL, PROBE_TOKEN


@shared_task()
def schedule_messages():
    """
    Эта таска выбирает все активные рассылки, время старта коих меньше или равно текущему времени,
    а время окончания больше или равно текущему времени.
    Для каждой такой рассылки выбираются все клиенты, у которых указаны теги или код оператора, как в рассылке.
    Далее для каждого такого клиента создается сообщение, которое привязывается к рассылке.
    Если время окончания рассылки меньше текущего времени, то статус сообщения будет "cancelled",
    иначе "pending".
    """
    broadcasts = Broadcast.objects.filter(
        Q(start_time__lte=timezone.now()) & Q(end_time__gte=timezone.now())
    ).exclude(messages__status__in=[Message.STATUS_SENT, Message.STATUS_CANCELLED]).distinct()

    for broadcast in broadcasts:
        logging.debug('Scheduling messages for broadcast with id {}.'.format(broadcast.id))
        if dangling_messages := Message.objects.filter(
                Q(broadcast=broadcast) & Q(status=Message.STATUS_PENDING) &
                (~Q(client__tags__in=broadcast.tags.all()) &
                 ~Q(client__operator_code__in=broadcast.operators.values_list('code', flat=True)))).distinct():
            dangling_messages.update(status=Message.STATUS_CANCELLED)
            logging.debug('Cancelled {} dangling messages for broadcast with id {}.'.format(dangling_messages, broadcast.id))
        clients = Client.objects.filter(
            Q(tags__in=broadcast.tags.all()) | Q(operator_code__in=broadcast.operators.values_list('code', flat=True))
        ).distinct().exclude(pk__in=broadcast.messages.values_list('client__pk', flat=True))
        now = timezone.now()
        batch = list(
            Message(
                broadcast=broadcast,
                client=client,
                status=Message.STATUS_PENDING if broadcast.end_time > now else Message.STATUS_CANCELLED
            ) for client in clients
        )
        Message.objects.bulk_create(batch)
        logging.debug('Created {} messages for broadcast with id {}.'.format(len(batch), broadcast.id))


@shared_task()
def send_messages():
    """
    Эта таска выбирает сообщения, которые еще не были отправлены, и отправляет их в Probe.
    За раз отправляется не более 30 сообщений.
    При этом сообщения выбираются по следующим критериям:
    1. Сообщение находится в статусе pending или failed.
    2. Время начала рассылки меньше или равно текущему времени.
    3. Время окончания рассылки больше или равно текущему времени.
    """
    # TODO: вынести ограничение на количество отправляемых за раз сообщений в настройки.
    messages = Message.objects.filter(status__in=[Message.STATUS_PENDING, Message.STATUS_FAILED],
                                      broadcast__start_time__lte=timezone.now(),
                                      broadcast__end_time__gte=timezone.now())[0:30]
    for message in messages:
        deliver_message.delay(message.id)


@shared_task()
def deliver_message(message_id):
    """
    Эта таска отправляет сообщение в Probe и обновляет статус сообщения в зависимости от ответа Probe.
    Ответ Probe записывается в БД в поле response.
    """
    try:
        message = Message.objects.get(id=message_id)
    except Message.DoesNotExist:
        logging.error('Message with id {} does not exist.'.format(message_id))
        return
    url = f'{PROBE_URL}/{message.id}'
    auth_header = {'Authorization': f'Bearer {PROBE_TOKEN}'}
    headers = {'Content-Type': 'application/json', **auth_header}
    payload = {
        'id': message.id,
        'phone': message.client.phone,
        'text': message.broadcast.text,
    }
    logging.debug('Sending message with id {} to probe.'.format(message_id))
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
    except requests.exceptions.RequestException as e:
        logging.error('Could not send message with id {} to probe: {}'.format(message_id, e))
        message.status = Message.STATUS_FAILED
        message.response = str(e)
        message.save()
        return
    response_text = response.text
    logging.debug('Probe response: {}'.format(response_text))
    if response.status_code == 200:
        message.status = Message.STATUS_SENT
        message.response = response_text
        message.save()
        logging.info('Message with id {} was successfully delivered.'.format(message_id))
    else:
        message.status = Message.STATUS_FAILED
        message.response = response_text
        message.save()
        logging.error('Message with id {} was not delivered.'.format(message_id))
