"""Классификатор писем по категориям.

Автор: Нефедов Алексей Геннадьевич (студ. билет 70200291).
Тема ВКР: «Разработка AI-приложения для анализа почтовых сообщений».
Направление 09.03.03 Прикладная информатика, профиль «Искусственный
интеллект и анализ данных».

Модель: TF-IDF + логистическая регрессия. Выбор обусловлен двумя
соображениями. Первое — необходимость автономной работы без GPU и без
обращений к облачным LLM, что диктуется политикой конфиденциальности
почты. Второе — прозрачность логики: линейная модель поверх TF-IDF
легко интерпретируется, её вес для каждого слова можно вывести в
отчёт, чего нельзя сказать о трансформерах.

Математически классификатор устроен так. Входной текст s
преобразуется в TF-IDF-вектор x ∈ ℝ^V, где V — размер словаря n-грамм
(1–2-грамм). Логистическая регрессия для класса c оценивает
вероятность P(c | x) = softmax(W_c · x + b_c). Во время обучения
оптимизируется штраф L2 на весах и отрицательный log-likelihood.

Интерфейс модуля сознательно тонкий, чтобы заменить реализацию на
BERT-ru или rubert-tiny можно было без правки потребителей
(AnalysisService, REST API, клиент).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from email_analyzer.db.models import Category


# Seed-набор для обучения. Объём подобран так, чтобы на каждый класс
# приходилось не менее 15 примеров: это минимум, при котором
# стратифицированная кросс-валидация 5 × 5 начинает работать устойчиво.
SEED_DATASET: List[Tuple[str, Category]] = [
    # ----- WORK (работа) -----
    ("Совещание перенесено на понедельник, 10:00.", Category.WORK),
    ("Прошу согласовать договор с контрагентом до среды.", Category.WORK),
    ("Отчёт по проекту готов, ссылка на Google Docs внутри.", Category.WORK),
    ("Напоминание: завтра ежемесячный обзор команды.", Category.WORK),
    ("Просьба подписать документ во вложении.", Category.WORK),
    ("Смета согласована, приступаем к реализации.", Category.WORK),
    ("Прошу прислать статус по задаче до конца дня.", Category.WORK),
    ("Планёрка завтра в 09:30, повестка прикреплена.", Category.WORK),
    ("Отправляю протокол последней встречи для ознакомления.", Category.WORK),
    ("Презентацию к понедельнику, аудитория — заказчик.", Category.WORK),
    ("Встреча с подрядчиком состоится в четверг.", Category.WORK),
    ("Please review the draft presentation by EOD.", Category.WORK),
    ("Reminder: weekly standup tomorrow at 10 AM.", Category.WORK),
    ("Status update needed for Q2 deliverables.", Category.WORK),
    ("Sprint planning is moved to Thursday afternoon.", Category.WORK),
    ("Звонок клиенту перенесён на пятницу.", Category.WORK),
    ("Пожалуйста, добавь меня в рассылку по проекту.", Category.WORK),

    # ----- PERSONAL (личное) -----
    ("Поздравляю с днём рождения! Желаю всего самого лучшего.", Category.PERSONAL),
    ("Мам, привет. Как дела? Напиши, как будет минутка.", Category.PERSONAL),
    ("Собираемся в субботу на даче, присоединяйся!", Category.PERSONAL),
    ("Фото с отпуска прикрепил, смотри :)", Category.PERSONAL),
    ("Увидимся в кино в семь часов?", Category.PERSONAL),
    ("Забыл зонт у тебя в квартире, заберу в выходные.", Category.PERSONAL),
    ("Спасибо за подарок, он шикарный!", Category.PERSONAL),
    ("Позвони, как будет время, есть новости.", Category.PERSONAL),
    ("Встретимся в пятницу?", Category.PERSONAL),
    ("Happy birthday! Have a wonderful day.", Category.PERSONAL),
    ("Hey, are you free for coffee this weekend?", Category.PERSONAL),
    ("Miss you, talk soon!", Category.PERSONAL),
    ("Мы с Мишей едем на море, присоединяйся.", Category.PERSONAL),
    ("Спасибо, что выручил в ту пятницу.", Category.PERSONAL),
    ("Поболтаем в воскресенье?", Category.PERSONAL),
    ("Завтра у бабушки юбилей, не забудь.", Category.PERSONAL),

    # ----- PROMO (реклама) -----
    ("Скидка 50% только сегодня! Успей купить.", Category.PROMO),
    ("Новая коллекция уже в продаже. Бесплатная доставка.", Category.PROMO),
    ("Промокод SALE20 на любой заказ.", Category.PROMO),
    ("Подпишись на рассылку и получай эксклюзивные акции.", Category.PROMO),
    ("Супер распродажа! Скидки до 70% на всё.", Category.PROMO),
    ("Подарочный сертификат в подарок при покупке от 3000 руб.", Category.PROMO),
    ("Чёрная пятница: цены зачёркнуты, срок ограничен.", Category.PROMO),
    ("Только для вас — индивидуальная скидка 25%.", Category.PROMO),
    ("Мегаскидка на смартфоны, торопись.", Category.PROMO),
    ("Хочешь первым узнавать о новинках? Оформи подписку.", Category.PROMO),
    ("Summer sale — up to 70% off, limited time offer.", Category.PROMO),
    ("Use promo code SUMMER15 for extra discount.", Category.PROMO),
    ("Free shipping this weekend only!", Category.PROMO),
    ("Last chance to grab your favorite items at 40% off.", Category.PROMO),
    ("Эксклюзивное предложение для постоянных клиентов.", Category.PROMO),
    ("Подарок-сертификат! Забери до конца недели.", Category.PROMO),

    # ----- SPAM (спам) -----
    ("СРОЧНО! Вы выиграли миллион, перейдите по ссылке прямо сейчас!!!", Category.SPAM),
    ("Получите кредит без проверки, 0%, оформление онлайн.", Category.SPAM),
    ("Viagra очень дёшево, закажи сейчас, доставка бесплатная.", Category.SPAM),
    ("ВЫИГРЫШ!!! Вам причитается приз, напишите адрес.", Category.SPAM),
    ("Быстрый заработок от 5000$ в день, без вложений.", Category.SPAM),
    ("Уникальный шанс удвоить капитал за неделю!", Category.SPAM),
    ("Казино онлайн — получи бонус 10000 рублей.", Category.SPAM),
    ("Сниму проклятие, приворот, гадание 100% результат.", Category.SPAM),
    ("You won the lottery! Click the link to claim.", Category.SPAM),
    ("Make money fast, no experience required!!!", Category.SPAM),
    ("Hot girls want to meet you tonight!", Category.SPAM),
    ("Buy cheap pills without prescription, discreet delivery.", Category.SPAM),
    ("Казино выигрыш бонус немедленно", Category.SPAM),
    ("Получите приз без обмана, нужно только подтверждение.", Category.SPAM),
    ("ЗАБЕРИТЕ ВАШ БЕСПЛАТНЫЙ ПОДАРОК СЕЙЧАС!!!", Category.SPAM),
    ("Денежные переводы без комиссии, без паспорта.", Category.SPAM),

    # ----- PHISHING (фишинг) -----
    ("Ваш банк заблокировал карту. Срочно введите данные по ссылке.", Category.PHISHING),
    ("Подтвердите пароль Google, иначе аккаунт будет удалён.", Category.PHISHING),
    ("Верификация карты требует ввода CVV по ссылке ниже.", Category.PHISHING),
    ("PayPal: подозрительная активность, войдите для подтверждения.", Category.PHISHING),
    ("Ваш налоговый возврат готов, подтвердите реквизиты.", Category.PHISHING),
    ("Приём посылки: обновите данные на сайте по ссылке.", Category.PHISHING),
    ("Обнаружен вход с нового устройства, проверьте и подтвердите.", Category.PHISHING),
    ("Amazon: заказ приостановлен, подтвердите платёжный метод.", Category.PHISHING),
    ("Verify your bank account by clicking the link.", Category.PHISHING),
    ("Your Apple ID has been locked. Confirm your identity.", Category.PHISHING),
    ("We detected unusual activity on your Microsoft account.", Category.PHISHING),
    ("Your password will expire in 24 hours, reset now.", Category.PHISHING),
    ("Требуется немедленно подтвердить платёж", Category.PHISHING),
    ("Ваш Госуслуги аккаунт заблокирован, перейдите по ссылке.", Category.PHISHING),
    ("Обновите данные СБП, иначе переводы будут приостановлены.", Category.PHISHING),
    ("Ссылка для входа в интернет-банк истекает через час.", Category.PHISHING),

    # ----- IMPORTANT (важное) -----
    ("Кандидат прошёл итоговое собеседование, ждём решения.", Category.IMPORTANT),
    ("ВНИМАНИЕ: на сервере обнаружена критическая уязвимость.", Category.IMPORTANT),
    ("Срок сдачи отчёта — завтра до 18:00, напоминаю.", Category.IMPORTANT),
    ("Получено разрешение регулятора, можно запускать.", Category.IMPORTANT),
    ("Авария в продакшене, нужна ваша помощь немедленно.", Category.IMPORTANT),
    ("Суд назначил заседание на следующий понедельник.", Category.IMPORTANT),
    ("Подтверждён контракт на 15 миллионов, детали внутри.", Category.IMPORTANT),
    ("Инвестор согласился, готовим документы к подписи.", Category.IMPORTANT),
    ("Critical security patch available — update now.", Category.IMPORTANT),
    ("Incident P1 raised in production, on-call required.", Category.IMPORTANT),
    ("Board meeting scheduled for Friday, attendance mandatory.", Category.IMPORTANT),
    ("Compliance audit starts tomorrow, prepare documents.", Category.IMPORTANT),
    ("Важная новость: компания выиграла тендер.", Category.IMPORTANT),
    ("Юридический запрос, ответ требуется в течение суток.", Category.IMPORTANT),
    ("Договор расторгнут в одностороннем порядке.", Category.IMPORTANT),
    ("Подтверждение брони на рейс не получено, проверьте.", Category.IMPORTANT),

    # ----- OTHER (прочее) -----
    ("Добрый день! Хотел уточнить, получили ли вы наш ответ.", Category.OTHER),
    ("Подтверждаю получение вашего сообщения.", Category.OTHER),
    ("Извините за задержку, вышлю ответ завтра.", Category.OTHER),
    ("Прикладываю файл с дополнительной информацией.", Category.OTHER),
    ("По поводу расписания, уточните у коллег.", Category.OTHER),
    ("Записался на курс, начало 5 октября.", Category.OTHER),
    ("Thanks for the update, will get back to you.", Category.OTHER),
    ("FYI — forwarding this for your reference.", Category.OTHER),
    ("Just checking in, any progress on this?", Category.OTHER),
    ("Quick note: meeting moved by 15 minutes.", Category.OTHER),
    ("Запрос принят, номер обращения 123456.", Category.OTHER),
    ("Ответ на ваш запрос в обработке.", Category.OTHER),
    ("Добавил вас в рассылку по событиям отрасли.", Category.OTHER),
    ("Не забудьте обновить статус на портале.", Category.OTHER),
    ("Проверьте, пожалуйста, расписание и подтвердите.", Category.OTHER),
]


@dataclass(frozen=True, slots=True)
class ClassificationResult:
    category: Category
    confidence: float
    top_scores: Tuple[Tuple[Category, float], ...]


def _normalize(text: str) -> str:
    """Приведение текста к единому виду перед векторизацией.

    URL и адреса почты заменяются на маркеры, чтобы конкретное имя
    домена не влияло на классификацию. Лишние пробелы схлопываются.
    Регистр приводится к нижнему.
    """
    text = text.lower()
    text = re.sub(r"https?://\S+", " url ", text)
    text = re.sub(r"\S+@\S+", " email ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


class EmailClassifier:
    """Классификатор писем."""

    def __init__(self, model_path: Optional[Path] = None) -> None:
        self.model_path = model_path
        self._pipeline: Optional[Pipeline] = None
        self._categories: List[Category] = []

    # ---------- Обучение ----------

    def fit(
        self,
        texts: Sequence[str],
        labels: Sequence[Category],
    ) -> None:
        if len(texts) != len(labels):
            raise ValueError("len(texts) != len(labels)")
        if len(set(labels)) < 2:
            raise ValueError("need ≥ 2 distinct categories to train")

        normalized = [_normalize(t) for t in texts]
        # Объединяем слово- и символ-n-граммы. Символьные граммы хорошо
        # справляются с русской морфологией (выигр, скидк, заблокир) без
        # явной лемматизации.
        features = FeatureUnion([
            ("word", TfidfVectorizer(
                analyzer="word", ngram_range=(1, 2),
                min_df=1, sublinear_tf=True,
            )),
            ("char", TfidfVectorizer(
                analyzer="char_wb", ngram_range=(3, 5),
                min_df=1, sublinear_tf=True,
            )),
        ])
        self._pipeline = Pipeline(
            steps=[
                ("features", features),
                ("clf", LogisticRegression(
                    max_iter=2000, class_weight="balanced", C=4.0,
                )),
            ]
        )
        self._pipeline.fit(normalized, [c.value for c in labels])
        self._categories = sorted(
            {Category(c) for c in self._pipeline.classes_},
            key=lambda c: c.value,
        )

    def fit_seed(self) -> None:
        """Обучение на встроенном seed-наборе."""
        texts = [t for t, _ in SEED_DATASET]
        labels = [c for _, c in SEED_DATASET]
        self.fit(texts, labels)

    # ---------- Сохранение ----------

    def save(self, path: Optional[Path] = None) -> Path:
        target = path or self.model_path
        if target is None:
            raise ValueError("model path not specified")
        target.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self._pipeline, target)
        return target

    def load(self, path: Optional[Path] = None) -> None:
        source = path or self.model_path
        if source is None or not source.exists():
            raise FileNotFoundError(f"model file not found: {source}")
        self._pipeline = joblib.load(source)
        self._categories = sorted(
            {Category(c) for c in self._pipeline.classes_},
            key=lambda c: c.value,
        )

    # ---------- Инференс ----------

    def is_fitted(self) -> bool:
        return self._pipeline is not None

    def predict(self, text: str) -> ClassificationResult:
        if not self.is_fitted():
            raise RuntimeError("classifier is not fitted, call fit()/fit_seed() first")
        assert self._pipeline is not None

        normalized = _normalize(text)
        proba = self._pipeline.predict_proba([normalized])[0]
        classes = [Category(c) for c in self._pipeline.classes_]

        pairs = sorted(
            zip(classes, proba, strict=True),
            key=lambda p: p[1],
            reverse=True,
        )
        best_category, best_confidence = pairs[0]
        return ClassificationResult(
            category=best_category,
            confidence=float(best_confidence),
            top_scores=tuple((c, float(p)) for c, p in pairs),
        )
