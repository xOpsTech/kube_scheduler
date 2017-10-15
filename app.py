from pymongo import MongoClient
import pykube_util
import constatnts
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
from pytz import utc

client = MongoClient(constatnts.MONGO_IP, 27017)
db = client['xops']
tenant_collection = db['tenants']


def read_services():
    for tenant in tenant_collection.find():
        services = tenant.get('services')
        tenant_id = tenant.get('id')
        # print tenant

        if services:
            print("processing for " + tenant_id)
            act_on_services(tenant_id, services)


def act_on_services(tenant_id, services):
    for service in services:
        service_name = service.get('service')
        service_started = service.get('service_started')
        if service_started is False:
            print('deploying ' + service_name)
            service['tenant'] = tenant_id

            # configs_json = {
            #     'tenant': tenant_id,
            #     'url': service.get('url'),
            #     'username': service.get('username'),
            #     'password': service.get('password')
            # }

            pykube_util.deploy(service)
            print('deployed %s successfully' % service_name)
            update_doc(tenant_id)
        else:
            print("%s is already deployed for tenant %s" % (service_name, tenant_id))


def update_doc(tenant_id):
    tenant_collection.update(
        {"_id": tenant_id, "services.service_started": False},
        {"$set": {"services.$.service_started": True}}
    )
    print('updated db')


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
