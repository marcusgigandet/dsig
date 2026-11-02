FROM espressif/idf:v6.1

# Run IDF script to export environment variables
RUN printf '\n. /opt/esp/idf/export.sh > /dev/null\n' >> /root/.bashrc

ENV CCACHE_DIR=/root/.cache/ccache
