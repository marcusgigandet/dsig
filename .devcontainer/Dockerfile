FROM espressif/idf:v6.1

# Stable paths for editor extensions, independent of Python/tool versions.
RUN ln -s /opt/esp/python_env/idf*_env /opt/esp/python \
    && ln -s /opt/esp/tools/esp-clangd/*/esp-clangd/bin/clangd /usr/local/bin/clangd

# Source and CMake checks used by cmake-tooling.
RUN apt-get update \
    && apt-get install -y --no-install-recommends clang-format clang-tidy clangd \
    && rm -rf /var/lib/apt/lists/* \
    && /opt/esp/python/bin/python -m pip install --no-cache-dir cmakelang==0.6.13

# Avoid repeated RFC2217 negotiation when esptool changes its read timeout.
COPY serial /opt/esp/serial
RUN /opt/esp/python/bin/python /opt/esp/serial/install.py

# Run IDF script to export environment variables
RUN printf '\n. /opt/esp/idf/export.sh > /dev/null\n' >> /root/.bashrc

ENV CCACHE_DIR=/root/.cache/ccache
