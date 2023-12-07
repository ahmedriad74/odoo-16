FROM odoo:latest

USER root
		
RUN set -x; \
	apt-get update \
		&& pip3 install --upgrade xlrd xmltodict \
		# && apt-get install python-openpyxl python3-openpyxl -y
# RUN pip3 install pandas
# USER odoo