// Copyright 2019 The Opt Authors. All rights reserved.
// Use of this source code is governed by a BSD-style
// license that can be found in the LICENSE file.

package opt // import "modernc.org/opt"

import (
	"reflect"
	"strings"
	"testing"
)

func Test(t *testing.T) {
	set := NewSet()
	set.Arg("std", true, func(opt, val string) error {
		if strings.HasPrefix(val, "=") {
			t.Errorf("%q %q", opt, val)
		}
		return nil
	})
	if err := set.Parse([]string{
		"-std=c99",
		"-std c99",
	}, func(opt string) error {
		t.Errorf("%q", opt)
		return nil
	}); err != nil {
		t.Error(err)
	}
}

func TestParser(t *testing.T) {
	// We use a pointer for 'h' so we can distinguish between:
	// nil = flag not provided
	// "" = flag provided without an argument (-h)
	// "val" = flag provided with an argument (-h=val)
	type config struct {
		o    bool
		a    string
		h    *string
		args []string // Captures unprocessed/positional arguments
	}

	tests := []struct {
		name    string
		args    []string
		want    config
		wantErr bool
	}{
		{
			name: "empty",
			args: []string{},
			want: config{},
		},
		{
			name: "option o",
			args: []string{"-o"},
			want: config{o: true},
		},
		{
			name: "arg a separated",
			args: []string{"-a", "foo"},
			want: config{a: "foo"},
		},
		{
			name: "arg a with equals",
			args: []string{"-a=foo"},
			want: config{a: "foo"},
		},
		{
			name:    "arg a missing value",
			args:    []string{"-a"},
			wantErr: true,
		},
		{
			name: "optional h without arg",
			args: []string{"-h"},
			want: config{h: stringPtr("")},
		},
		{
			name: "optional h with arg",
			args: []string{"-h=auto"},
			want: config{h: stringPtr("auto")},
		},
		{
			name: "optional h followed by positional",
			// Because -h is optional, "foo" should NOT be consumed by -h.
			// It should fall through to the positional argument handler.
			args: []string{"-h", "foo"},
			want: config{h: stringPtr(""), args: []string{"foo"}},
		},
		{
			name: "hybrid combination",
			args: []string{"-o", "-h=auto", "-a", "bar", "baz"},
			want: config{o: true, h: stringPtr("auto"), a: "bar", args: []string{"baz"}},
		},
		{
			name: "positional arguments only",
			args: []string{"file1.c", "file2.c"},
			want: config{args: []string{"file1.c", "file2.c"}},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			var c config
			set := NewSet()

			// Define Option 'o'
			set.Opt("o", func(opt string) error {
				c.o = true
				return nil
			})

			// Define Arg 'a' (imm=false)
			set.Arg("a", false, func(opt, arg string) error {
				c.a = arg
				return nil
			})

			// Define OptionalArg 'h'
			set.OptionalArg("h", func(opt, arg string) error {
				c.h = &arg
				return nil
			})

			// Parse handles unprocessed arguments
			err := set.Parse(tt.args, func(arg string) error {
				c.args = append(c.args, arg)
				return nil
			})

			if (err != nil) != tt.wantErr {
				t.Errorf("Parse() error = %v, wantErr %v", err, tt.wantErr)
				return
			}

			if !tt.wantErr && !reflect.DeepEqual(c, tt.want) {
				t.Errorf("Parse() got state = %+v, want %+v", c, tt.want)
				// Helper to print pointer values nicely if tests fail
				if c.h != nil && tt.want.h != nil && *c.h != *tt.want.h {
					t.Errorf("  h difference: got %q, want %q", *c.h, *tt.want.h)
				}
			}
		})
	}
}

// stringPtr is a quick helper to get a pointer to a string literal
func stringPtr(s string) *string {
	return &s
}
