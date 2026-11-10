CC         := emcc
CXX        := em++
TARGET     := triangle

SRC_C      := src/main.c src/asset.c src/framebuffer.c src/pass.c src/capture.c \
              src/sh.c src/sg.c src/texture.c src/mesh.c src/ground.c src/shadow.c \
              src/probe_grid.c src/tri_grid.c src/bloom.c src/hdr_env.c \
              src/instanced_mesh.c src/cgltf_impl.c src/stb_image_impl.c src/audio.c
SRC_CPP    := src/physics.cpp

OBJ_C      := $(SRC_C:.c=.o)
OBJ_CPP    := $(SRC_CPP:.cpp=.o)
OBJ_ALL    := $(OBJ_C) $(OBJ_CPP)

SHELL_HTML := shell/index.html
OUT        := $(TARGET).html

CFLAGS  := -O3 -Wall -Wextra -Wno-unused-parameter -Ithird_party -Isrc -sUSE_BULLET=1

LDFLAGS := \
    -sUSE_GLFW=3 \
    -sFULL_ES3=1 \
    -sMIN_WEBGL_VERSION=2 \
    -sMAX_WEBGL_VERSION=2 \
    -sALLOW_MEMORY_GROWTH=1 \
    -sINITIAL_MEMORY=256MB \
    -sSTACK_SIZE=1MB \
    --preload-file shaders@/shaders \
    --preload-file assets@/assets \
    -sUSE_BULLET=1 \
    --shell-file $(SHELL_HTML)

.PHONY: all clean serve run

all: $(OUT)

$(OUT): $(OBJ_ALL) $(wildcard src/*.h) $(SHELL_HTML) $(wildcard shaders/*) $(wildcard assets/*)
	$(CXX) $(OBJ_ALL) -o $(OUT) $(LDFLAGS)

$(OBJ_C): %.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

$(OBJ_CPP): %.o: %.cpp
	$(CXX) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJ_ALL) $(TARGET).js $(TARGET).wasm $(TARGET).data $(TARGET).html

serve:
	@echo "http://localhost:8000/$(TARGET).html"
	@python3 -m http.server 8000

run: all serve
