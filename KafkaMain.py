# alternatively to the REST API
# one can use Kafka messages to configure mqtt-rest
# This file is he mqtt-manager kafka entry point
# the purpose of functions here is to verify input and pass
# the requests to the controller class
import logging
import kafka
import json
from time import sleep

import conf
import DeviceController as dc

LOGGER = logging.getLogger('mqtt-manager.' + __name__)
LOGGER.addHandler(logging.StreamHandler())
LOGGER.setLevel(logging.DEBUG)


def KafkaConsumerLoop():
    while True:
        # To consume latest messages and auto-commit offsets
        while True:
            try:
                consumer = (kafka.
                            KafkaConsumer('dojot.device-manager.device',
                                          group_id='mqtt-manager',
                                          bootstrap_servers=[conf.kafkaHost]))
                break
            except kafka.errors.NoBrokersAvailable:
                LOGGER.error('Could not connect to Kafka at %s.'
                             ' Chances are the server is not ready yet.'
                             ' Will retry in 30sec' % conf.kafkaHost)
                sleep(30)

        LOGGER.debug("waiting for new messages")
        for message in consumer:
            try:
                requestData = json.loads(message.value)
            except ValueError:
                LOGGER.error('Could not decode message as JSON. '
                             + dumpKafkaMessage(message))
                continue

            # check if message have all the needed params
            deviceInfo = checkMessageParams(message, requestData)
            if not deviceInfo:
                continue

            if deviceInfo['action'] in ['create', 'update']:
                try:
                    dc.addDeviceACLRequest(deviceInfo)
                    LOGGER.info('device %s created' % deviceInfo['device'])
                except dc.RequestError as err:
                    LOGGER.error(err.message + " "
                                 + dumpKafkaMessage(message))

            elif deviceInfo['action'] == 'delete':
                try:
                    dc.removeDeviceACLRequest(deviceInfo)
                    LOGGER.info("Device %s removed from ACL"
                                % deviceInfo['device'])
                except dc.RequestError as err:
                    LOGGER.error(err.message + " "
                                 + dumpKafkaMessage(message))

            else:
                LOGGER.error("'event' " + requestData['event']
                             + " not implemented"
                             + dumpKafkaMessage(message))


# helper function to log messages (for debug purposes)
def dumpKafkaMessage(msg):
    return ('%s:%d:%d: key=%s value=%s'
            % (msg.topic, msg.partition,
               msg.offset, msg.key,
               msg.value)
            )


def checkMessageParams(message, requestData):
    deviceInfo = {}
    # some sanity checks on kafka message fields
    # get device name and topic
    if 'event' not in requestData.keys():
        LOGGER.error('event not specified. '
                     + dumpKafkaMessage(message))
        return None
    deviceInfo['action'] = requestData['event']

    if 'data' not in requestData.keys():
        LOGGER.error("data segment not found. "
                     + dumpKafkaMessage(message))
        return None
    if 'id' not in requestData['data'].keys():
        LOGGER.error("device id not specified. "
                     + dumpKafkaMessage(message))
        return None
    deviceInfo['device'] = requestData['data']['id']

    if 'meta' not in requestData.keys():
        LOGGER.error("meta segment not found. "
                     + dumpKafkaMessage(message))
        return None
    if 'service' not in requestData['meta'].keys():
        LOGGER.error("service not specified. "
                     + dumpKafkaMessage(message))
        return None
    deviceInfo['topic'] = ('/' + requestData['meta']['service']
                           + '/' + requestData['data']['id']
                           + '/attrs')

    return deviceInfo


KafkaConsumerLoop()
