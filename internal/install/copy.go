package install

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	"ai-agents/internal/files"
)

func copyMarkdownDir(srcDir, dstDir, label string, opts Options, reader *bufio.Reader) (int, error) {
	entries, err := os.ReadDir(srcDir)
	if err != nil {
		if os.IsNotExist(err) {
			return 0, nil
		}
		return 0, fmt.Errorf("read %s: %w", srcDir, err)
	}

	var names []string
	for _, entry := range entries {
		if entry.IsDir() || filepath.Ext(entry.Name()) != ".md" {
			continue
		}
		names = append(names, entry.Name())
	}
	sort.Strings(names)

	count := 0
	for _, name := range names {
		copied, err := copyWithOverwrite(filepath.Join(srcDir, name), filepath.Join(dstDir, name), label+"/"+name, opts, reader)
		if err != nil {
			return 0, err
		}
		if copied {
			count++
		}
	}
	return count, nil
}

func copyChildDirs(srcDir, dstDir, label string, opts Options, reader *bufio.Reader) (int, error) {
	entries, err := os.ReadDir(srcDir)
	if err != nil {
		if os.IsNotExist(err) {
			return 0, nil
		}
		return 0, fmt.Errorf("read %s: %w", srcDir, err)
	}

	var names []string
	for _, entry := range entries {
		if entry.IsDir() {
			names = append(names, entry.Name())
		}
	}
	sort.Strings(names)

	count := 0
	for _, name := range names {
		copied, err := copyWithOverwrite(filepath.Join(srcDir, name), filepath.Join(dstDir, name), label+"/"+name, opts, reader)
		if err != nil {
			return 0, err
		}
		if copied {
			count++
		}
	}
	return count, nil
}

func copyWithOverwrite(src, dst, label string, opts Options, reader *bufio.Reader) (bool, error) {
	info, err := os.Stat(src)
	if err != nil {
		if os.IsNotExist(err) {
			return false, nil
		}
		return false, fmt.Errorf("stat source %s: %w", src, err)
	}

	if _, err := os.Lstat(dst); err == nil {
		overwrite := opts.Force
		if !overwrite {
			answer, err := prompt(reader, opts.Stdout, fmt.Sprintf("Overwrite %s? [y/N]: ", label))
			if err != nil {
				return false, err
			}
			overwrite = strings.EqualFold(answer, "y")
		}
		if !overwrite {
			fmt.Fprintf(opts.Stdout, "Skipped %s\n", label)
			return false, nil
		}
		if err := os.RemoveAll(dst); err != nil {
			return false, fmt.Errorf("remove existing %s: %w", dst, err)
		}
	} else if err != nil && !os.IsNotExist(err) {
		return false, fmt.Errorf("stat destination %s: %w", dst, err)
	}

	if info.IsDir() {
		if err := files.CopyDir(src, dst); err != nil {
			return false, err
		}
	} else {
		if err := files.CopyFile(src, dst); err != nil {
			return false, err
		}
	}
	return true, nil
}
