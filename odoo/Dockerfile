FROM odoo:16.0

USER root
		
RUN set -x; \
	apt-get update \
		&& pip3 install --upgrade xlrd xmltodict \
		&& pip3 --no-cache-dir install \
			openpyxl \
			pillow
# RUN pip3 install pandas
# USER odoo