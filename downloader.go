// Simple downloader example using go

package main

import "syscall"
import "unsafe"
import "golang.org/x/sys/windows"

type StartupInfoEx struct {
	windows.StartupInfo
	AttributeList *PROC_THREAD_ATTRIBUTE_LIST
}

type PROC_THREAD_ATTRIBUTE_LIST struct {
	dwFlags  uint32
	size     uint64
	count    uint64
	reserved uint64
	unknown  *uint64
	entries  []*PROC_THREAD_ATTRIBUTE_ENTRY
}

type PROC_THREAD_ATTRIBUTE_ENTRY struct {
	attribute *uint32
	cbSize    uintptr
	lpValue   uintptr
}

var (
    urlmonDLL = syscall.NewLazyDLL("urlmon.dll")
    procURLDownloadToFileW = urlmonDLL.NewProc("URLDownloadToFileW")
    
    kernel32DLL = syscall.NewLazyDLL("kernel32.dll")
    procCreateProcessW = kernel32DLL.NewProc("CreateProcessW")
)


func DownloadAndLaunch(url string, filename string) {
    url16, _ := syscall.UTF16PtrFromString(url)
    filename16, _ := syscall.UTF16PtrFromString(filename)
    r0, _, _ := procURLDownloadToFileW.Call(
        uintptr(0),
        uintptr(unsafe.Pointer(url16)),
        uintptr(unsafe.Pointer(filename16)),
        0,
        uintptr(0))
    if r0 == 0 {
        var procInfo windows.ProcessInformation
        var startupInfo StartupInfoEx
        startupInfo.Cb = uint32(unsafe.Sizeof(startupInfo))
        
        cmd := "cmd /c foo.exe"
        cmd16, _ := syscall.UTF16PtrFromString(cmd)
        
        procCreateProcessW.Call(
            uintptr(0),
            uintptr(unsafe.Pointer(cmd16)),
            uintptr(0),
            uintptr(0),
            uintptr(0),
            uintptr(0),
            uintptr(0),
            uintptr(0),
            uintptr(unsafe.Pointer(&startupInfo)),
            uintptr(unsafe.Pointer(&procInfo)))
    }
}

func main() {
    DownloadAndLaunch("https://www.7-zip.org/a/7z1900.exe", "7z1900.exe");
}