from pymongo import MongoClient
import pykube_util
import constatnts
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from pytz import utc

client = MongoClient(constatnts.MONGO_IP, 27017)
db = client['xops']
tenant_collection = db['tenants']
compulsory_services_collection = db['compulsory_services']


def read_services():
    for tenant in tenant_collection.find():
        services = tenant.get('services')
        tenant_id = tenant.get('id')
        # print tenant

        if services:
            print("processing for " + tenant_id)
            act_on_services(tenant_id, services)


def act_on_services(tenant_id, services):
    user_service_set = set()
    for service in services:
        user_service_set.add(service.get('serviceId'))
        service_name = service.get('service')
        service_started = service.get('service_started')
        if service_started is False:
            print('deploying ' + service_name)
            service['tenant'] = tenant_id

            pykube_util.deploy(service)
            print('deployed %s successfully' % service_name)
            update_doc(tenant_id)
        else:
            print("%s is already deployed for tenant %s" % (service_name, tenant_id))

    start_compulsory_services(tenant_id, user_service_set)


def update_doc(tenant_id):
    tenant_collection.update(
        {"_id": tenant_id, "services.service_started": False},
        {"$set": {"services.$.service_started": True}}
    )
    print('updated db')


def add_doc(tenant_id, json_to_add):
    tenant_collection.update(
        {"_id": tenant_id},
        {"$push": {"services": json_to_add}}
    )
    print('added to db')


def start_compulsory_services(tenant_id, user_service_set):
    for compulsory_service in compulsory_services_collection.find():
        compulsory_service_id = compulsory_service.get('serviceId')

        if compulsory_service_id not in user_service_set:
            service_name = compulsory_service.get('service')
            service_json = {'tenant': tenant_id, 'service': service_name}
            pykube_util.deploy(service_json)
            print('deployed compulsory service %s successfully' % service_name)

            json_to_add = {'serviceId': compulsory_service_id, 'service': service_name, 'service_started': True,
                           "active": True}
            add_doc(tenant_id, json_to_add)


# read_services()

if __name__ == '__main__':
    print('Starting kube scheduler')
    SCHEDULER_INTERVAL = constatnts.SCHEDULER_INTERVAL
    executors = {
        'default': ThreadPoolExecutor()
    }
    app_scheduler = BlockingScheduler(executors=executors, timezone=utc)

    app_scheduler.add_job(read_services, 'interval', seconds=SCHEDULER_INTERVAL, id='kubernetes deployment scheduler')
    app_scheduler.start()
