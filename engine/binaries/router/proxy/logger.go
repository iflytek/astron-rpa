package proxy

import (
	"fmt"
)

// Logger defines a minimal logging interface.
type Logger interface {
	Infof(format string, args ...interface{})
	Errorf(format string, args ...interface{})
}

// BaseLogger is a simple Logger implementation using fmt.Printf.
type BaseLogger struct{}

// Infof logs an info message.
func (l *BaseLogger) Infof(format string, args ...interface{}) {
	fmt.Printf(format, args...)
}

// Errorf logs an error message.
func (l *BaseLogger) Errorf(format string, args ...interface{}) {
	fmt.Printf(format, args...)
}
