package internal

import (
	"encoding/binary"
	"errors"
	"os"
	"unsafe"
)

// StdIoConn wraps communication over stdin/stdout using the native
// messaging protocol (length-prefixed binary framing).
type StdIoConn struct {
}

// NewStdIoConn creates a new StdIoConn instance.
func NewStdIoConn() *StdIoConn {
	return &StdIoConn{}
}

// InitByteOrder detects host byte order so we can read/write lengths correctly.
func InitByteOrder() binary.ByteOrder {
	var one int16 = 1
	b := (*byte)(unsafe.Pointer(&one))
	if *b == 0 {
		return binary.BigEndian
	} else {
		return binary.LittleEndian
	}
}

var NativeByteOrder = InitByteOrder()
// ExitError indicates a normal shutdown triggered by stdin closure.
var ExitError = errors.New("normal exit")

func (s *StdIoConn) Write(msg []byte) error {
	// write message length header
	err := binary.Write(os.Stdout, NativeByteOrder, uint32(len(msg)))
	if err != nil {
		return err
	}

	_, err = os.Stdout.Write(msg)
	if err != nil {
		return err
	}
	return nil
}

func (s *StdIoConn) Read() ([]byte, error) {
	// read message length in native byte order
	var length uint32
	err := binary.Read(os.Stdin, NativeByteOrder, &length)
	if err != nil {
		return nil, ExitError
	}

	buff := make([]byte, length)
	if length == 0 {
		return buff, nil
	}

	_, err = os.Stdin.Read(buff)
	if err != nil {
		return nil, err
	}
	return buff, nil
}
