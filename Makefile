CORE_COMPONENTS =  utils/decaf-utils-rabbitmq
CORE_COMPONENTS += utils/decaf-utils-rpc
CORE_COMPONENTS += utils/decaf-utils-ioloop
CORE_COMPONENTS += utils/decaf-utils-components
CORE_COMPONENTS += utils/decaf-utils-protocol-stack
CORE_COMPONENTS += components/decaf-componentmanager
CORE_COMPONENTS += components/decaf-oscar
CORE_COMPONENTS += components/decaf-cli
COMPONENTS = utils/decaf-utils-vnfm
COMPONENTS += components/decaf-specification
COMPONENTS += components/decaf-placement
COMPONENTS += components/decaf-masta
COMPONENTS += components/decaf-storage
COMPONENTS += components/decaf-deployment
COMPONENTS += components/decaf-vnf-manager-adapter
COMPONENTS += components/example-scaling


.PHONY: all core-all core-clean core-install core-sdist clean install sdist dirs

all: core-all
	for i in $(COMPONENTS); do make -C $$i; done

core-all:
	exec /bin/bash ./scripts/create_dirs.sh
	for i in $(CORE_COMPONENTS); do make -C $$i; done

core-clean:
	for i in $(CORE_COMPONENTS); do make -C $$i clean; done

core-install:
	exec /bin/bash ./scripts/create_dirs.sh
	for i in $(CORE_COMPONENTS); do make -C $$i install; done

core-sdist:
	for i in $(CORE_COMPONENTS); do make -C $$i sdist; done

clean: core-clean
	for i in $(COMPONENTS); do make -C $$i clean; done

install: core-install
	for i in $(COMPONENTS); do make -C $$i install; done

sdist: core-sdist
	for i in $(COMPONENTS); do make -C $$i sdist; done

dirs:
	exec /bin/bash ./scripts/create_dirs.sh