// OPUS: Echo of Starsong — 언어(currentLanguage) 변경 도구
//
// OPTIONINFO 파일은 Base64로 인코딩된 UTF-8 JSON(CRLF)이다.
// 이 도구는 그 안의 "currentLanguage" 정수값 '딱 하나'만 정확히 교체한다.
// (다른 옵션/포맷/줄바꿈은 바이트 그대로 보존)
//
// 사용:
//   더블클릭 → 메뉴에서 언어 선택
//   set-opus-language.exe                 (기본 경로 자동 탐색, 메뉴)
//   set-opus-language.exe -lang 1         (비대화형: EN 으로 설정)
//   set-opus-language.exe -file "<경로>"  (OPTIONINFO 경로 수동 지정)
package main

import (
	"bufio"
	"encoding/base64"
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"strconv"
	"strings"
	"syscall"
	"time"
)

// Sigono.Utilities.Localization.EnumLanguage (Sigono.Utilities.dll 에서 추출)
type lang struct {
	id   int
	code string
	name string
	note string
}

var languages = []lang{
	{0, "CHT", "번체 중국어", "원본 지원"},
	{1, "EN", "영어", "원본 지원"},
	{2, "CHS", "간체 중국어", "원본 지원"},
	{3, "JP", "일본어", "원본 지원"},
	{8, "KR", "한국어", "한글 패치 적용 시에만"},
	{4, "FR", "프랑스어", "데이터 없음(빈 화면 주의)"},
	{5, "BR", "브라질 포르투갈어", "데이터 없음(빈 화면 주의)"},
	{6, "ES", "스페인어", "데이터 없음(빈 화면 주의)"},
	{7, "PT", "포르투갈어", "데이터 없음(빈 화면 주의)"},
	{9, "DE", "독일어", "데이터 없음(빈 화면 주의)"},
	{10, "JPSWITCH", "일본어(Switch)", "데이터 없음(빈 화면 주의)"},
}

var langRe = regexp.MustCompile(`("currentLanguage"\s*:\s*)(-?\d+)`)

func langByID(id int) *lang {
	for i := range languages {
		if languages[i].id == id {
			return &languages[i]
		}
	}
	return nil
}

// Windows 콘솔에서 한글이 깨지지 않도록 UTF-8 코드페이지로 전환
func enableUTF8Console() {
	k := syscall.NewLazyDLL("kernel32.dll")
	k.NewProc("SetConsoleOutputCP").Call(65001)
	k.NewProc("SetConsoleCP").Call(65001)
}

func defaultOptionInfoPath() string {
	home, err := os.UserHomeDir()
	if err != nil {
		return ""
	}
	return filepath.Join(home, "AppData", "LocalLow", "SIGONO",
		"OPUS_ Echo of Starsong", "Save", "OPTIONINFO")
}

func pause() {
	fmt.Print("\n계속하려면 Enter 키를 누르세요...")
	bufio.NewReader(os.Stdin).ReadString('\n')
}

func fail(interactive bool, format string, a ...any) {
	fmt.Printf("\n[오류] "+format+"\n", a...)
	if interactive {
		pause()
	}
	os.Exit(1)
}

func main() {
	enableUTF8Console()

	filePtr := flag.String("file", "", "OPTIONINFO 파일 경로 (미지정 시 기본 위치 자동 탐색)")
	langPtr := flag.Int("lang", -1, "설정할 언어 enum 값 (지정 시 메뉴 없이 바로 적용)")
	flag.Parse()

	interactive := *langPtr < 0

	path := *filePtr
	if path == "" {
		path = defaultOptionInfoPath()
	}

	fmt.Println("=== OPUS: Echo of Starsong — 언어 변경 도구 ===")
	fmt.Printf("대상 파일: %s\n", path)

	raw, err := os.ReadFile(path)
	if err != nil {
		fail(interactive, "OPTIONINFO 파일을 열 수 없습니다: %v\n"+
			"       게임을 한 번 실행한 적이 있는지, 경로가 맞는지 확인하세요.\n"+
			"       (-file \"<경로>\" 로 직접 지정할 수 있습니다)", err)
	}

	decoded, err := base64.StdEncoding.DecodeString(strings.TrimSpace(string(raw)))
	if err != nil {
		fail(interactive, "Base64 디코딩 실패(파일 형식이 예상과 다릅니다): %v", err)
	}
	json := string(decoded)

	matches := langRe.FindAllStringSubmatchIndex(json, -1)
	if len(matches) != 1 {
		fail(interactive, "\"currentLanguage\" 항목을 정확히 1개 찾지 못했습니다(발견: %d개). 중단합니다.", len(matches))
	}
	curVal, _ := strconv.Atoi(langRe.FindStringSubmatch(json)[2])

	curName := "알 수 없음"
	if l := langByID(curVal); l != nil {
		curName = fmt.Sprintf("%s (%s)", l.code, l.name)
	}
	fmt.Printf("현재 언어: %d = %s\n", curVal, curName)

	target := *langPtr
	if interactive {
		target = promptMenu()
	}

	sel := langByID(target)
	if sel == nil {
		fail(interactive, "유효하지 않은 언어 값입니다: %d", target)
	}

	if target == curVal {
		fmt.Printf("\n이미 %s (%s) 상태입니다. 변경할 내용이 없습니다.\n", sel.code, sel.name)
		if interactive {
			pause()
		}
		return
	}

	// 백업 (타임스탬프)
	backup := path + ".bak-" + time.Now().Format("20060102-150405")
	if err := os.WriteFile(backup, raw, 0644); err != nil {
		fail(interactive, "백업 생성 실패: %v", err)
	}

	// currentLanguage 정수값 하나만 교체 (그룹1=키/공백 보존, 값만 치환)
	newJSON := langRe.ReplaceAllString(json, "${1}"+strconv.Itoa(target))
	newB64 := base64.StdEncoding.EncodeToString([]byte(newJSON))
	if err := os.WriteFile(path, []byte(newB64), 0644); err != nil {
		fail(interactive, "파일 쓰기 실패: %v", err)
	}

	// 검증: 다시 읽어 값 확인
	verifyRaw, _ := os.ReadFile(path)
	verifyDec, _ := base64.StdEncoding.DecodeString(strings.TrimSpace(string(verifyRaw)))
	verifyVal, _ := strconv.Atoi(langRe.FindStringSubmatch(string(verifyDec))[2])

	fmt.Printf("\n[완료] 언어를 %d = %s (%s) 으로 변경했습니다.\n", target, sel.code, sel.name)
	fmt.Printf("       검증 통과: 현재 파일의 currentLanguage = %d\n", verifyVal)
	fmt.Printf("       백업: %s\n", backup)
	if sel.id != 0 && sel.id != 1 && sel.id != 2 && sel.id != 3 && sel.id != 8 {
		fmt.Println("       주의: 이 언어는 원본에 텍스트 데이터가 없어 빈 화면이 될 수 있습니다.")
	}
	if interactive {
		pause()
	}
}

func promptMenu() int {
	fmt.Println("\n변경할 언어를 선택하세요:")
	for i, l := range languages {
		fmt.Printf("  %2d) %-8s %-10s  [%s]\n", i+1, l.code, l.name, l.note)
	}
	reader := bufio.NewReader(os.Stdin)
	for {
		fmt.Print("\n번호 입력 (취소: q): ")
		line, err := reader.ReadString('\n')
		if err != nil {
			os.Exit(0)
		}
		s := strings.TrimSpace(line)
		if s == "q" || s == "Q" {
			fmt.Println("취소되었습니다.")
			os.Exit(0)
		}
		n, err := strconv.Atoi(s)
		if err != nil || n < 1 || n > len(languages) {
			fmt.Println("  잘못된 입력입니다. 목록의 번호를 입력하세요.")
			continue
		}
		return languages[n-1].id
	}
}
