# Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2023 Marine Institute
#       Diego Pereiro Rodriguez
#
#       diego.pereiro@marine.ie
#
#   This library is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this library.  If not, see <http://www.gnu.org/licenses/>.
#   --------------------------------------------------------------------

FROM python:3.12

MAINTAINER Diego Pereiro Rodriguez <Diego.Pereiro@Marine.ie>

RUN apt-get update && apt-get -y install cron vim

# Directory to store logging files
RUN mkdir /log

WORKDIR /root

COPY [ "*.nc" , "." ]

# Install required packages
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY config .

# Set cron
COPY crontab /etc/cron.d/crontab
RUN chmod 0644 /etc/cron.d/crontab
RUN /usr/bin/crontab /etc/cron.d/crontab

COPY [ "*.py" , "." ]

RUN echo $PYTHONPATH

CMD ["cron", "-f"]
