all: submit

submit: submit.c
	gcc -o submit submit.c
	chmod 755 submit
	chmod u+s submit
	chmod 700 submit.py
	chmod 600 submit_config.json

.PHONY: clean
clean:
	rm -f submit
