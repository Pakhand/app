Запрос.Текст ="ВЫБРАТЬ
	              |	&Дата КАК TIME_ID,
	              |	СвободныеОстаткиОстатки.Склад КАК Склад,
	              |	СвободныеОстаткиОстатки.ВНаличииОстаток КАК STOCK,
	              |	СвободныеОстаткиОстатки.ВРезервеСоСкладаОстаток + СвободныеОстаткиОстатки.ВРезервеПодЗаказОстаток КАК REZERV,
	              |	СвободныеОстаткиОстатки.Номенклатура КАК Номенклатура,
	              |	ВЗЦены.ЦенаКорп КАК price_corp,
	              |	ВЗЦены.ЦенаОпт КАК price_opt,
	              |	ВЗЦены.ЦенаПС КАК UNITCOST,
	              |	ВЗЦены.ЦенаРозница КАК price_retail,
	              |	ВЗЦены.ЦенаСайт КАК price_site
	              |ИЗ
	              |	РегистрНакопления.СвободныеОстатки.Остатки(&Дата, ) КАК СвободныеОстаткиОстатки
	              |		ЛЕВОЕ СОЕДИНЕНИЕ (ВЫБРАТЬ
	              |			ЕСТЬNULL(ЦеныНоменклатурыСрезПоследнихКорп.Цена, 0) КАК ЦенаКорп,
	              |			ЕСТЬNULL(ЦеныНоменклатурыСрезПоследнихОпт.Цена, 0) КАК ЦенаОпт,
	              |			ЕСТЬNULL(ЦеныНоменклатурыСрезПоследнихПС.Цена, 0) КАК ЦенаПС,
	              |			ЕСТЬNULL(ЦеныНоменклатурыСрезПоследнихРозница.Цена, 0) КАК ЦенаРозница,
	              |			ЕСТЬNULL(ЦеныНоменклатурыСрезПоследнихСайт.Цена, 0) КАК ЦенаСайт,
	              |			Товары.Ссылка КАК Ссылка
	              |		ИЗ
	              |			Справочник.Номенклатура КАК Товары
	              |				ПОЛНОЕ СОЕДИНЕНИЕ РегистрСведений.ЦеныНоменклатуры.СрезПоследних(&Дата, ВидЦены = &ВидЦеныРозница) КАК ЦеныНоменклатурыСрезПоследнихРозница
	              |				ПО Товары.Ссылка = ЦеныНоменклатурыСрезПоследнихРозница.Номенклатура
	              |				ПОЛНОЕ СОЕДИНЕНИЕ РегистрСведений.ЦеныНоменклатуры.СрезПоследних(&Дата, ВидЦены = &ВидЦеныОпт) КАК ЦеныНоменклатурыСрезПоследнихОпт
	              |				ПО Товары.Ссылка = ЦеныНоменклатурыСрезПоследнихОпт.Номенклатура
	              |				ПОЛНОЕ СОЕДИНЕНИЕ РегистрСведений.ЦеныНоменклатуры.СрезПоследних(&Дата, ВидЦены = &ВидЦеныКорп) КАК ЦеныНоменклатурыСрезПоследнихКорп
	              |				ПО Товары.Ссылка = ЦеныНоменклатурыСрезПоследнихКорп.Номенклатура
	              |				ПОЛНОЕ СОЕДИНЕНИЕ РегистрСведений.ЦеныНоменклатуры.СрезПоследних(&Дата, ВидЦены = &ВидЦеныПС) КАК ЦеныНоменклатурыСрезПоследнихПС
	              |				ПО Товары.Ссылка = ЦеныНоменклатурыСрезПоследнихПС.Номенклатура
	              |				ПОЛНОЕ СОЕДИНЕНИЕ РегистрСведений.ЦеныНоменклатуры.СрезПоследних(&Дата, ВидЦены = &ВидЦеныСайт) КАК ЦеныНоменклатурыСрезПоследнихСайт
	              |				ПО Товары.Ссылка = ЦеныНоменклатурыСрезПоследнихСайт.Номенклатура
	              |		ГДЕ
	              |			Товары.ЭтоГруппа = ЛОЖЬ
	              |			И Товары.ПометкаУдаления = ЛОЖЬ) КАК ВЗЦены
	              |		ПО СвободныеОстаткиОстатки.Номенклатура = ВЗЦены.Ссылка
	              |
	              |УПОРЯДОЧИТЬ ПО
	              |	Склад,
	              |	Номенклатура";
