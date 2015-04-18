LIB_DIR=$(shell pwd)/open/lib
OBJ=daoke_libs

help:
	-@./help.sh

all:$(OBJ)
	-@echo "Done All!"

daoke_libs:
	$(MAKE) -C $(LIB_DIR) all



clean:
	$(MAKE) -C $(LIB_DIR) clean

distclean:
	$(MAKE) -C $(LIB_DIR) clean
	rm -rf open/lib/polarssl-1.2.8/



tag:
	git tag -a "ngxapi_1.0.4.131202_Beta" -m "ngxapi_1.0.4.131202_Beta"
	git push origin --tags
	
push:
	git push origin HEAD:refs/for/master

