__author__ = 'sdjoum'



# decaf_specification = Specification()
# # res, object1 = decaf_specification.parser('dataplaneVNF2.yaml', vnfd_schema_v01)
# res, object1 = decaf_specification.parser('complex.yaml', nsd_schema)
# print object1

# placement = Placement()
# print placement.new_vnf(nfvo_tenant="d9a225dc-69ef-11e5-8abd-f4b7e264b599", vnf_descriptor= object1)

# placement.create_scenario(nfvo_tenant_id="d9a225dc-69ef-11e5-8abd-f4b7e264b599", topo=object1)

import decaf.utils.rabbitmq.rpc_layer.rpc_layer as rpc

def printer(x):

    print str(x)

def after_specification(response):
    print str(response)
    place = r.call("create_scenario", nfvo_tenant_id="d9a225dc-69ef-11e5-8abd-f4b7e264b599", topo=response[1])
    place.addCallback(after_placement2)



def after_placement(response):

    print str(response)
    # create one scenario with this vnf


def after_placement2(response):
    #
    # print str(response)
    d = r.call("deployment", deploy_graph=response[1])
    d.addCallback(printer)
    # deploy created scenario



r = rpc.RpcLayer()

spec = r.call("parser", filePath='complex.yaml', schema=nsd_schema)
spec.addCallback(after_specification)


print "Im waiting for JAVA, this may takes a while"

# d.addCallback(printer)
