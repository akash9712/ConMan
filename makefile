CFLAGS=-g
CC=g++
DEPS=mount.h
TARGET=con

con: $(DEPS) $(TARGET).cpp
	${CC} -o $(TARGET) $(TARGET).cpp ${CFLAGS}