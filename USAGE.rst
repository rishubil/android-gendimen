사용방법
====
기본적인 사용법은 주석 사이에 ``{* expr *}`` 와 같은 표현식을 삽입하여 동작합니다.

.. code-block:: xml

	<dimen name="margin_small">8dp</dimen>
	
	<!-- {* margin_small * 2 *} -->
	<dimen name="margin_large">0dp</dimen><!-- 결과: 16dp -->

gendimen에서는 대입 연산자로서 ``<=``를 사용합니다. 만약 해당 표현식이 적용될
dimen tag의 바로 윗줄에 작성되어 있다면 대입 연산자와 값을 대입할 dimen tag의 name을
생략해서 사용할 수 있습니다.

반대로, 값을 대입할 dimen tag의 name과 대입 연산자 ``<=``를 포함한다면 표현식이 해당
dimen tag의 바로 윗줄 아닌 문서의 어느 위치에 존재해도 괜찮습니다.

.. code-block:: xml

	<!-- {* margin_large <= margin_small * 2 *} -->
	<dimen name="margin_small">8dp</dimen>
	<dimen name="margin_large">0dp</dimen><!-- 결과: 16dp -->

새로운 관계를 가지는 dimen tag를 추가하고 싶다면, 해당 dimen tag의 값을 비워둔 채
작성한 후 gendimen.py를 실행하면, 참조하는 dimen tag의 단위와 동일하게 새 dimen tag의
단위를 지정해줍니다. 그러나, 두 개 이상의 서로 다른 단위를 가지는 dimen tag를 참조할
경우, 오류가 발생합니다.

만약 -f 또는 --force 옵션을 사용하여 실행한 경우 해당 오류가 발생하더라도 무시하고 단위를
지정합니다. 이 때, 새 dimen tag에 적용되는 단위는 표현식에서 가장 마지막에 있는 표현식의
단위를 따릅니다.

.. code-block:: xml

	<!-- {* margin_small * 2 *} -->
	<dimen name="margin_small">8dp</dimen>
	<dimen name="margin_large"></dimen><!-- 결과: 16dp -->

또, 표현식에서 어떠한 다른 dimen tag도 참조하지 않았고, dimen tag에도 단위를 지정하지
않았다면 오류가 발생하지는 않지만 실행 뒤에도 dimen tag에 단위가 지정되지 않습니다. 대신
어떠한 다른 dimen tag도 참조하지 않았을 경우 dimen tag에 값 없이 단위만 지정해 놓으면
해당 단위를 사용합니다.

.. code-block:: xml

	<!-- {* 1 + 2 *} -->
	<dimen name="unit_empty"></dimen><!-- 결과: 3 (단위 없음) -->
	
	<!-- {* 1 + 2 *} -->
	<dimen name="unit_set">dp</dimen><!-- 결과: 3dp -->

표현식은 내부적으로 python eval 명령어를 통해 실행됩니다. 따라서, 한 줄에 작성할 수 있는
표현식이라면 어떤 python 코드라도 자유롭게 사용할 수 있습니다.

.. code-block:: xml

	<!-- {* sum(x for x in range(20) if x % 3 == 1) *} -->
	<dimen name="something_interesting">dp</dimen><!-- 결과: 70dp -->

## 주의사항
*	서로 다른 단위끼리는 연산할 수 없습니다.

	.. code-block:: xml

		<dimen name="text_size">24sp</dimen>
		<dimen name="padding">8dp</dimen>
	
		<!-- {* text_size + padding *} : ERROR! -->
		<dimen name="new_dimen">8dp</dimen>

	단, gendimen.py를 실행할 때, command line option으로 -f 또는 --force 옵션을
	추가한 경우 경고는 출력되지만 무시하고 덮어 쓸 수 있습니다.

	또, 해당 dimen tag에 단위가 존재하지 않을 경우, 단위가 존재하는 dimen tag의 값을
	연산하면 해당 dimen tag의 단위로 자동 변경됩니다.

*	기준이 불명확한 상호참조는 사용할 수 없습니다.

	아래와 같은 경우, foo, bar, fuz 세 dimen tag 중 기준값을 결정할 수 없으므로 오류가
	발생합니다.

	.. code-block:: xml

		<!-- {* foo = bar + fuz *} : ERROR! -->
		<dimen name="foo">4dp</dimen>
		<!-- {* bar = fuz *} : ERROR! -->
		<dimen name="bar">8dp</dimen>
		<!-- {* fuz = foo *} : ERROR! -->
		<dimen name="fuz">6dp</dimen>


*	한 주석에서는 가장 첫 표현식만 연산되며, 나머지는 평가되지 않습니다.

	아래와 같은 경우 오류 없이 실행되지만, 두 번째 표현식은 무시됩니다.

	.. code-block:: xml

		<dimen name="margin_small">8dp</dimen>
	
		<!-- {* margin_small * 2 *}  {* it = doesn't + matter *} -->
		<dimen name="margin_large">0dp</dimen>


*	정수 몫을 구할 때에는 `//` 연산자를, 실수 나눗셈에는 `/` 연산자를 사용합니다.

	.. code-block:: xml

		<!-- {* 3 / 2 *} -->
		<dimen name="foo">dp</dimen><!-- 결과: 1.5dp -->
		<!-- {* 3 // 2 *} -->
		<dimen name="bar">0dp</dimen><!-- 결과: 1dp -->


Command line options
--------------------
*	-y, --yes

	수정사항 적용 여부를 묻지 않고 바로 적용합니다.

*	-f, --force

	서로 다른 단위끼리 연산할 경우에 오류를 무시하고 값을 대입합니다.
