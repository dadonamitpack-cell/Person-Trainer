# סנכרון אוטומטי וחינמי של Apple Watch

**איך זה עובד:** קיצור דרך (Shortcut) באייפון רץ פעם ביום, אוסף מ-Health את נתוני היום, ושומר קובץ קטן
ב-`logs/watch/` בריפו הזה דרך ה-API של GitHub. Claude קורא את הקבצים ומריץ `scripts/watch_summary.py`
כדי לראות מגמות. הכול חינמי: אפליקציית קיצורי הדרך מובנית באייפון, וה-API של GitHub חינמי.

> ⚠️ **לפני הכול: להפוך את הריפו לפרטי.** כרגע הריפו **ציבורי**, וכל אחד יכול לקרוא אותו, כולל הדופק,
> השינה, המשקל ודף הפיזיותרפיה. ב-GitHub: Settings ← General ← Danger Zone ← Change visibility ← Private.
> ריפו פרטי חינמי. **לא להפעיל את הסנכרון כל עוד הריפו ציבורי.**

## שלב 1: טוקן ל-GitHub (פעם אחת)
1. GitHub ← תמונת הפרופיל ← Settings ← Developer settings ← Personal access tokens ← **Fine-grained tokens** ← Generate new token.
2. Repository access: **Only select repositories** ← `Person-Trainer` בלבד.
3. Permissions ← Repository permissions ← **Contents: Read and write**. שום הרשאה אחרת.
4. תוקף: עד שנה. לשים תזכורת ביומן לחדש.
5. להעתיק את הטוקן (מתחיל ב-`github_pat_`). **לא לשלוח אותו בצ'אט ולא לשמור אותו בריפו**, רק בתוך הקיצור.

הטוקן יכול לכתוב רק לריפו הזה. אם הטלפון אבד, מבטלים אותו באותו מסך.

## שלב 2: בניית הקיצור באפליקציית Shortcuts
קיצור חדש בשם **Watch Sync**. שמות הפעולות כאן באנגלית. אם הטלפון בעברית, השמות יהיו מתורגמים, ואפשר
לחפש אותם בשורת החיפוש של הפעולות. בכל פעם שכתוב "שמור כמשתנה" משתמשים ב-**Set Variable**.

**תאריך**
1. `Current Date` ← `Format Date`: Custom, `yyyy-MM-dd` ← שמור כמשתנה `day`.

**דופק מנוחה**
2. `Find Health Samples`: Type = **Resting Heart Rate**, Start Date **is today**, Sort by Start Date, Latest First, Limit 1.
3. `Get Details of Health Sample` ← **Value** ← שמור כ-`rhr`.

**HRV**
4. `Find Health Samples`: Type = **Heart Rate Variability**, Start Date **is in the last 1 days**.
5. `Get Details of Health Sample` ← Value ← `Calculate Statistics` ← **Average** ← שמור כ-`hrv`.

**שינה**
6. `Find Health Samples`: Type = **Sleep Analysis**, Start Date **is in the last 1 days**.
   אם יש אפשרות להוסיף תנאי על Value, להוסיף **Value is not In Bed** ו-**Value is not Awake**.
7. `Get Details of Health Sample` ← **Duration** ← `Calculate Statistics` ← **Sum** ← שמור כ-`sleep`.
   (לא משנה אם יוצא בשעות, דקות או שניות. הסקריפט מזהה וממיר.)

**צעדים, דקות אימון, דופק מקסימלי**
8. `Find Health Samples`: **Steps**, is today ← Get Details: Value ← Calculate Statistics: **Sum** ← `steps`.
9. `Find Health Samples`: **Exercise Minutes** (נקרא גם Exercise Time), is today ← Value ← **Sum** ← `exmin`.
10. `Find Health Samples`: **Heart Rate**, is today ← Value ← **Maximum** ← `hrmax`.

**VO2max ומשקל (אם יש)**
11. `Find Health Samples`: **VO2 Max** (Cardio Fitness), is in the last 30 days, Latest First, Limit 1 ← Value ← `vo2`.
12. `Find Health Samples`: **Weight**, is in the last 1 days, Latest First, Limit 1 ← Value ← `weight`.

**בניית הקובץ ושליחה**
13. `Dictionary` עם המפתחות (Text) והמשתנים:
    `date`=day, `rhr`=rhr, `hrv`=hrv, `sleep_h`=sleep, `steps`=steps, `exercise_min`=exmin,
    `hr_max`=hrmax, `vo2max`=vo2, `weight`=weight.
14. `Text` ← לבחור בתוכו את ה-Dictionary (זה הופך אותו ל-JSON).
15. `Base64 Encode` ← Line Breaks: **None** ← שמור כ-`b64`.
16. `Get Contents of URL`:
    - URL: `https://api.github.com/repos/dadonamitpack-cell/Person-Trainer/contents/logs/watch/[day].json`
      (להכניס את המשתנה `day` במקום `[day]`)
    - Method: **PUT**
    - Headers: `Authorization` = `Bearer github_pat_...` · `Accept` = `application/vnd.github+json`
    - Request Body: **JSON**, שני שדות Text: `message` = `watch [day]` · `content` = `b64`

**בדיקה:** להריץ ידנית פעם אחת. אם הצליח, יופיע קובץ חדש ב-`logs/watch/` ב-GitHub.
להריץ פעם שנייה באותו יום נכשל, וזה בסדר: הקובץ של היום כבר קיים.

## שלב 3: הפעלה אוטומטית
Shortcuts ← **Automation** ← + ← **Time of Day**: ‏22:30, כל יום ← Watch Sync ← **Run Immediately**.

שימו לב: iOS חוסם קריאה מ-Health כשהטלפון נעול. אם רוב הימים חסרים, מחליפים את הטריגר ל-**App**
("כשנפתחת אפליקציה" שפותחים כל ערב, למשל WhatsApp). זה רץ כשהטלפון פתוח, וההרצות הנוספות באותו יום
פשוט נכשלות בלי נזק.

## מה Claude עושה עם זה
- `python3 scripts/watch_summary.py` מציג טבלה שבועית ומשווה את 7 הימים האחרונים לממוצע של 4 השבועות שלפניהם.
- דגלים: דופק מנוחה גבוה ב-5+ פעימות מהבסיס, HRV מתחת לבסיס ביותר מסטיית תקן אחת, ממוצע שינה מתחת ל-7 שעות.
- הנתונים מחליפים את שדות הדופק, השינה והמשקל בצ'ק-אין השבועי. מה שעדיין צריך לכתוב ידנית:
  תחושה במשחק, עייפות, כאבים ועדכוני פיזיו.

הדגלים מבוססים על מגמה של שבוע ולא על יום בודד. ה-HRV של אפל (SDNN) רועש, וה-VO2max הוא הערכה בלבד
(טעות של כ-10–15%). לכן הם משמשים לזיהוי כיוון, לא כמספרים מדויקים.
