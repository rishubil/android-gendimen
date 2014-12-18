android-gendimen
================

Android에서 서로 관계있는 dimen의 값을 일일히 java 코드에서 지정하여 사용하는 것은 귀찮습니다.  
특히 아주 단순한 관계 - 예를 들면 height는 width의 2배라던가 하는 관계는 쓸데없이 코드를 복잡하게 만듭니다.  
그렇다면 dimen.xml에 미리 dimen간의 관계를 정의해놓으면 어떨까요?

android-gendimen은 dimen.xml 파일의 주석에 지정한 expresion을 분석하여 알아서 dimen값을 계산해주는 간단한 python 스크립트입니다.

## Quick start


### 1. Writing dimens.xml

``` xml
<resources>
    <dimen name="margin_small">8dp</dimen>

    <!-- two times of small margin {{ margin_small * 2 }} -->
    <dimen name="margin_large">0dp</dimen>
    
    <!-- {{ margin_largest = margin_small * 3 }} -->
    <dimen name="margin_largest">0dp</dimen>
    
    <!-- {{ ( margin_small + margin_largest ) / 2 }} -->
    <dimen name="margin_mean">0dp</dimen>
    
    <!-- {{ ( margin_small ** 2 ) / 3.0 }} -->
    <dimen name="complex_dimen">0dp</dimen>

</resources>
```

### 2. Run gendimen.py

	$ python gendimen.py <filepath of dimens.xml>
	
### 3. Check generated dimens

``` xml
<resources>
    <dimen name="margin_small">8dp</dimen>

    <!-- two times of small margin {{ margin_small * 2 }} -->
    <dimen name="margin_large">16dp</dimen>
    
    <!-- {{ margin_largest = margin_small * 3 }} -->
    <dimen name="margin_largest">24dp</dimen>
    
    <!-- {{ ( margin_small + margin_largest ) / 2 }} -->
    <dimen name="margin_mean">12dp</dimen>
    
    <!-- {{ ( margin_small ** 2 ) / 3.0 }} -->
    <dimen name="complex_dimen">21.333333333333332dp</dimen>

</resources>
```

	
## Usage
기본적인 사용법은 주석 사이에 ```{{ expr }}``` 와 같은 표현식을 삽입하여 동작합니다.

``` xml
<dimen name="margin_small">8dp</dimen>

<!-- {{ margin_large = margin_small * 2 }} -->
<dimen name="margin_large">0dp</dimen>
```

만약 수정할 dimen tag의 바로 위에 위치한 주석에 expr을 사용하는 경우라면, 좌측 표현식과 과 등호를 생략하고 사용할 수 있습니다.

``` xml
<dimen name="margin_small">8dp</dimen>

<!-- {{ margin_small * 2 }} -->
<dimen name="margin_large">0dp</dimen>
```

반대로, 좌측 표현식과 등호를 포함한다면 expr이 해당 dimen tag의 바로 위가 아닌 문서의 어느 위치에 존재해도 괜찮습니다.

``` xml
<!-- {{ margin_large = margin_small * 2 }} -->
<dimen name="margin_small">8dp</dimen>
<dimen name="margin_large">0dp</dimen>
```

#### 주의사항
* 서로 다른 단위끼리는 연산할 수 없습니다.
	``` xml
	<dimen name="text_size">24sp</dimen>
	<dimen name="padding">8dp</dimen>

	<!-- {{ new_dimen = text_size + padding }} : ERROR! -->
	<dimen name="new_dimen">8dp</dimen>
	```

* 무한 루프를 야기할 수 있는 상호참조는 사용할 수 없습니다.
	``` xml
	<!-- {{ foo = bar + fuz }} : ERROR! -->
	<dimen name="foo">4dp</dimen>
	<!-- {{ bar = fuz }} : ERROR! -->
	<dimen name="bar">8dp</dimen>
	<!-- {{ fuz = foo }} : ERROR! -->
	<dimen name="fuz">6dp</dimen>
	```

* 한 주석에서는 가장 첫 expr만 연산되며, 나머지는 평가되지 않습니다.
	``` xml
	<dimen name="margin_small">8dp</dimen>

	<!-- {{ margin_small * 2 }}  {{ it = doesn't + matter }} -->
	<dimen name="margin_large">0dp</dimen>
	```

* 계산된 결과의 단위는 기존 dimen tag에 사용하던 단위와 같으며, 아직 계산하지 않은 dimen tag라도 미리 사용할 단위를 명시해놓아야 합니다.
	``` xml
	<dimen name="margin_small">8dp</dimen>

	<!-- {{ margin_small * 2 }}
	<dimen name="margin_large">0</dimen> <!-- ERROR! -->
	```
