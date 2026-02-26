package internal

import (
	"context"
	"fmt"
	"log"
	"os"
)

// Logger defines a minimal logging interface used inside this module.
// The context parameter is kept for future extensions (e.g. tracing).
type Logger interface {
	Infof(ctx context.Context, format string, v ...interface{})
	Errorf(ctx context.Context, format string, v ...interface{})
}

// NewLogger returns a Logger writing to the given file.
func NewLogger(f *os.File) Logger {
	return &BaseLogger{
		log.New(f, "", log.LstdFlags),
	}
}

type BaseLogger struct {
	logger *log.Logger
}

// Infof logs an informational message.
func (l *BaseLogger) Infof(ctx context.Context, format string, args ...interface{}) {
	l.logger.Printf("[INFO] %v", fmt.Sprintf(format, args...))
}

// Errorf logs an error message.
func (l *BaseLogger) Errorf(ctx context.Context, format string, args ...interface{}) {
	l.logger.Printf("[ERRO] %v", fmt.Sprintf(format, args...))
}
