android-gendimen
================

Android에서 서로 관계있는 dimen의 값을 일일히 java 코드에서 지정하여 사용하는 것은
귀찮습니다.  
특히, 아주 단순한 관계 - 예를 들면 height는 width의 2배라던가 하는 관계는 쓸데없이
코드를 복잡하게 만듭니다.

그럼 dimen.xml에 dimen간의 관계를 정의해놓을 수 있다면 어떨까요?

android-gendimen은 dimen.xml 파일의 주석에 지정한 expresion을 분석하여 알아서
dimen값을 계산해주는 간단한 python 스크립트입니다.

## Quick start

### 1. dimens.xml 파일에 관계 지정

``` xml
<resources>
    <dimen name="margin_small">8dp</dimen>

    <!-- {* margin_small * 2 *} -->
    <dimen name="margin_large"></dimen>

    <!-- {* margin_large * 2 *} -->
    <dimen name="margin_largest"></dimen>

    <!-- {* margin_small * 0.8 *} -->
    <dimen name="shadow_small"></dimen>

    <!-- {* margin_large * 0.8 *} -->
    <dimen name="shadow_long"></dimen>

    <dimen name="base_font_size">11sp</dimen>

    <!-- {* base_font_size + 3 *} -->
    <dimen name="title_font_size"></dimen>

    <!-- {* base_font_size - 2 *} -->
    <dimen name="quote_font_size"></dimen>

    <dimen name="some_layout_width">120dp</dimen>
    <dimen name="some_layout_margin">8dp</dimen>

    <!-- {* (some_layout_width + some_layout_margin) / 2 *} -->
    <dimen name="some_layout_half_outer_width_with_margin"></dimen>

    <dimen name="equilateral_triangle_width">60dp</dimen>

    <!-- 정삼각형 높이 공식 {* equilateral_triangle_width * (3 ** 0.5) / 2 *} -->
    <dimen name="equilateral_triangle_height"></dimen>

    <!-- {* reduce(lambda x, y: 2 * y - x, [margin_small, margin_large, margin_largest]) *} -->
    <dimen name="crazy_dimension">dp</dimen>

    <!-- {* int("".join(str(x) for x in range(1, 4))) *} -->
    <dimen name="you_can_do_everything_what_you_want">dp</dimen>
</resources>

```

### 2. gendimen.py 실행

``` shell
$ python gendimen.py <filepath of dimens.xml>
```

### 3. 변경된 dimens.xml 파일 확인

``` xml
<resources>
    <dimen name="margin_small">8dp</dimen>

    <!-- {* margin_small * 2 *} -->
    <dimen name="margin_large">16dp</dimen>

    <!-- {* margin_large * 2 *} -->
    <dimen name="margin_largest">32dp</dimen>

    <!-- {* margin_small * 0.8 *} -->
    <dimen name="shadow_small">6.4dp</dimen>

    <!-- {* margin_large * 0.8 *} -->
    <dimen name="shadow_long">12.8dp</dimen>

    <dimen name="base_font_size">11sp</dimen>

    <!-- {* base_font_size + 3 *} -->
    <dimen name="title_font_size">14sp</dimen>

    <!-- {* base_font_size - 2 *} -->
    <dimen name="quote_font_size">9sp</dimen>

    <dimen name="some_layout_width">120dp</dimen>
    <dimen name="some_layout_margin">8dp</dimen>

    <!-- {* (some_layout_width + some_layout_margin) / 2 *} -->
    <dimen name="some_layout_half_outer_width_with_margin">64dp</dimen>

    <dimen name="equilateral_triangle_width">60dp</dimen>

    <!-- 정삼각형 높이 공식 {* equilateral_triangle_width * (3 ** 0.5) / 2 *} -->
    <dimen name="equilateral_triangle_height">51.9615242271dp</dimen>

    <!-- {* reduce(lambda x, y: 2 * y - x, [margin_small, margin_large, margin_largest]) *} -->
    <dimen name="crazy_dimension">40dp</dimen>

    <!-- {* int("".join(str(x) for x in range(1, 4))) *} -->
    <dimen name="you_can_do_everything_what_you_want">123dp</dimen>
</resources>

```


## 사용방법
기본적인 사용법은 주석 사이에 `{* expr *}` 와 같은 표현식을 삽입하여 동작합니다.

``` xml
<dimen name="margin_small">8dp</dimen>

<!-- {* margin_small * 2 *} -->
<dimen name="margin_large">0dp</dimen><!-- 결과: 16dp -->
```

android-gendimen에서는 대입 연산자로서 `<=`를 사용합니다. 만약 해당 표현식이 적용될
dimen tag의 바로 윗줄에 작성되어 있다면 대입 연산자와 값을 대입할 dimen tag의 name을
생략해서 사용할 수 있습니다.

반대로, 값을 대입할 dimen tag의 name과 대입 연산자 `<=`를 포함한다면 표현식이 해당
dimen tag의 바로 윗줄 아닌 문서의 어느 위치에 존재해도 괜찮습니다.

``` xml
<!-- {* margin_large <= margin_small * 2 *} -->
<dimen name="margin_small">8dp</dimen>
<dimen name="margin_large">0dp</dimen><!-- 결과: 16dp -->
```

더 자세한 사용 방법은 [USAGE.md](USAGE.md)를 참조하세요.
