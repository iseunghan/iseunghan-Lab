## 그룹 애너그램

### 초기 풀이
```java
class Solution {
    public List<List<String>> groupAnagrams(String[] strs) {
        // 문자열의 모든 수의 합을 구하면 될듯..?
        Map<Integer, List<String>> strings = new HashMap<>(strs.length);

        for (String s : strs) {
            int num = calcAllStrings(s);
            List<String> temp_list = strings.getOrDefault(num, new ArrayList<>());
            temp_list.add(s);
            strings.put(num, temp_list);
        }

        return strings.values()
                .stream().collect(Collectors.toList());
    }

    private int calcAllStrings(String s) {
        int result = 0;
        for (int i=0; i<s.length(); i++) {
            result += s.charAt(i);
        }
        System.out.println(s + " -> " + result);
        return result;
    }
}
```

- 55번 케이스에서 실패.
- 자릿수로 더하다보니, "duh", "ill" 두개가 동일한것으로 오판
- 자릿수는 안되겠다고 생각하고 포기.

