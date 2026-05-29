<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="ru_RU">

<!-- ══════════════════════════════════════════════════════════════ -->
<!-- Command names (context = command name)                        -->
<!-- ══════════════════════════════════════════════════════════════ -->
<context>
    <name>ThreadCreate</name>
    <message>
        <source>Create thread</source>
        <translation>Создать резьбу</translation>
    </message>
    <message>
        <source>Create a metric thread on a cylindrical face inside a PartDesign::Body</source>
        <translation>Создать метрическую резьбу на цилиндрической грани внутри PartDesign::Body</translation>
    </message>
</context>
<context>
    <name>ThreadInchCreate</name>
    <message>
        <source>Create inch thread</source>
        <translation>Создать дюймовую резьбу</translation>
    </message>
    <message>
        <source>Create an inch thread (UNC/UNF) on a cylindrical face inside a PartDesign::Body</source>
        <translation>Создать дюймовую резьбу (UNC/UNF) на цилиндрической грани внутри PartDesign::Body</translation>
    </message>
</context>

<!-- ══════════════════════════════════════════════════════════════ -->
<!-- Everything else — context ThreadWorkbench                     -->
<!-- ══════════════════════════════════════════════════════════════ -->
<context>
    <name>ThreadWorkbench</name>

    <!-- Workbench identity (InitGui.py module-level) -->
    <message>
        <source>Thread</source>
        <translation>Thread (Резьба)</translation>
    </message>
    <message>
        <source>Create metric (ISO 724) and inch (UNC/UNF) threads in PartDesign</source>
        <translation>Создание метрических (ISO 724) и дюймовых (UNC/UNF) резьб в PartDesign</translation>
    </message>

    <!-- UI: parameter group -->
    <message>
        <source>ParamGroup</source>
        <translation>Параметры резьбы</translation>
    </message>
    <message>
        <source>InchDiaLabel</source>
        <translation>Номинальный диаметр (дюйм):</translation>
    </message>
    <message>
        <source>InchTPILabel</source>
        <translation>TPI (витков/дюйм):</translation>
    </message>
    <message>
        <source>PitchMmLabel</source>
        <translation>Шаг (мм, расчётный):</translation>
    </message>
    <message>
        <source>Custom</source>
        <translation>— Кастомный —</translation>
    </message>
    <message>
        <source>DiameterLabel</source>
        <translation>Диаметр:</translation>
    </message>
    <message>
        <source>PitchLabel</source>
        <translation>Шаг (мм):</translation>
    </message>
    <message>
        <source>LengthLabel</source>
        <translation>Длина резьбы (мм):</translation>
    </message>
    <message>
        <source>OffsetLabel</source>
        <translation>Смещение от края (мм):</translation>
    </message>
    <message>
        <source>StartEdgeLabel</source>
        <translation>Начать от края:</translation>
    </message>
    <message>
        <source>NoEdge</source>
        <translation>— сначала выделите грань —</translation>
    </message>

    <!-- UI: direction group -->
    <message>
        <source>DirectionGroup</source>
        <translation>Направление</translation>
    </message>
    <message>
        <source>Reversed</source>
        <translation>Обратное направление (Reversed)</translation>
    </message>
    <message>
        <source>LeftHanded</source>
        <translation>Левая резьба (LeftHanded)</translation>
    </message>

    <!-- UI: chamfer group -->
    <message>
        <source>ChamferGroup</source>
        <translation>Фаска (на круглые рёбра перед резьбой)</translation>
    </message>
    <message>
        <source>AddChamfer</source>
        <translation>Добавить фаску</translation>
    </message>
    <message>
        <source>ChamferSize</source>
        <translation>Размер (мм):</translation>
    </message>

    <!-- UI: misc -->
    <message>
        <source>PresetLabel</source>
        <translation>Пресет:</translation>
    </message>
    <message>
        <source>TypeLabel</source>
        <translation>Тип:</translation>
    </message>
    <message>
        <source>External</source>
        <translation>Внешняя</translation>
    </message>
    <message>
        <source>Internal</source>
        <translation>Внутренняя</translation>
    </message>
    <message>
        <source>EdgeToEdge</source>
        <translation>От края до края (вся грань)</translation>
    </message>
    <message>
        <source>CreateButton</source>
        <translation>Создать резьбу</translation>
    </message>
    <message>
        <source>StatusDefault</source>
        <translation>Выберите цилиндрическую грань на объекте внутри PartDesign::Body</translation>
    </message>

    <!-- UI: live preview -->
    <message>
        <source>Live preview</source>
        <translation>Живой предпросмотр</translation>
    </message>

    <!-- Status messages -->
    <message>
        <source>status_two_edges</source>
        <translation>✓ Грань: R={radius:.2f} мм, длина грани ≈{face_len:.1f} мм. Края: #{idx0} и #{idx1}. Выберите стартовый край.</translation>
    </message>
    <message>
        <source>status_one_edge</source>
        <translation>✓ Грань: R={radius:.2f} мм. Найден 1 край #{idx0}. Выберите стартовый край.</translation>
    </message>
    <message>
        <source>status_no_edges</source>
        <translation>✓ Грань: R={radius:.2f} мм. Круглые края не найдены.</translation>
    </message>
    <message>
        <source>no_edges</source>
        <translation>— нет краёв —</translation>
    </message>

    <!-- Error messages -->
    <message>
        <source>ErrorTitle</source>
        <translation>Ошибка</translation>
    </message>
    <message>
        <source>err_no_document</source>
        <translation>Нет активного документа!</translation>
    </message>
    <message>
        <source>err_no_circular_edges</source>
        <translation>На выделенной грани не найдено круглых краёв!</translation>
    </message>
    <message>
        <source>err_no_start_edge</source>
        <translation>Выберите стартовый край!</translation>
    </message>
    <message>
        <source>err_edge_not_found</source>
        <translation>Выбранный край не найден!</translation>
    </message>
    <message>
        <source>TransactionName</source>
        <translation>Создать резьбу</translation>
    </message>
    <message>
        <source>done</source>
        <translation>✓ Резьба создана! Можно выбрать другую грань.</translation>
    </message>

    <!-- Builder errors -->
    <message>
        <source>err_nothing_selected</source>
        <translation>Ничего не выделено.</translation>
    </message>
    <message>
        <source>err_no_subelement</source>
        <translation>Не удалось определить выделенный элемент.</translation>
    </message>
    <message>
        <source>err_cannot_read_face</source>
        <translation>Не удалось прочитать грань.</translation>
    </message>
    <message>
        <source>err_not_cylindrical</source>
        <translation>Выделенная грань не цилиндрическая.</translation>
    </message>
    <message>
        <source>err_not_in_body</source>
        <translation>Объект не внутри PartDesign::Body.</translation>
    </message>
    <message>
        <source>err_not_enough_edges</source>
        <translation>Недостаточно краёв для авто-длины. Укажите длину резьбы вручную.</translation>
    </message>
    <message>
        <source>err_helix_failed</source>
        <translation>Не удалось создать спираль: {e}</translation>
    </message>
    <message>
        <source>err_unknown_profile</source>
        <translation>Неизвестный профиль резьбы: {pid}</translation>
    </message>

    <!-- InitGui log message -->
    <message>
        <source>Loading Thread module... done</source>
        <translation>Загрузка модуля Thread... готово</translation>
    </message>

</context>
</TS>
