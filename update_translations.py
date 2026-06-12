import os
import re

translations = {
    "as": {
        "gps_disabled": "স্থান সেৱা নিষ্ক্ৰিয় হৈ আছে। অনুগ্ৰহ কৰি কাৰ্য্য সম্পাদন কৰিবলৈ GPS সক্ষম কৰক।",
        "retry": "এতিয়াই পুনৰ চেষ্টা কৰক",
        "online_users": "অনলাইন ব্যৱহাৰকাৰী",
        "registered_users": "পঞ্জীয়নভুক্ত ব্যৱহাৰকাৰী",
        "issues_resolved": "সমাধান কৰা সমস্যাসমূহ",
        "cities": "চহৰসমূহ"
    },
    "bn": {
        "gps_disabled": "লোকেশন পরিষেবা নিষ্ক্রিয়। পদক্ষেপ নিতে দয়া করে GPS সক্ষম করুন।",
        "retry": "এখনই আবার চেষ্টা করুন",
        "online_users": "অনলাইন ব্যবহারকারী",
        "registered_users": "নিবন্ধিত ব্যবহারকারী",
        "issues_resolved": "সমাধান করা সমস্যা",
        "cities": "শহর"
    },
    "gu": {
        "gps_disabled": "સ્થાન સેવાઓ અક્ષમ છે. કૃપા કરીને ક્રિયાઓ કરવા માટે GPS સક્ષમ કરો।",
        "retry": "હમણાં ફરી પ્રયાસ કરો",
        "online_users": "ઓનલાઇન વપરાશકર્તાઓ",
        "registered_users": "નોંધાયેલા વપરાશકર્તાઓ",
        "issues_resolved": "ઉકેલાયેલી સમસ્યાઓ",
        "cities": "શહેરો"
    },
    "hi": {
        "gps_disabled": "लोकेशन सेवाएं अक्षम हैं। कृपया कार्रवाई करने के लिए GPS सक्षम करें।",
        "retry": "अभी पुन: प्रयास करें",
        "online_users": "ऑनलाइन उपयोगकर्ता",
        "registered_users": "पंजीकृत उपयोगकर्ता",
        "issues_resolved": "समाधान की गई समस्याएं",
        "cities": "शहर"
    },
    "kn": {
        "gps_disabled": "ಸ್ಥಳ ಸೇವೆಗಳನ್ನು ನಿಷ್ಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ. ಕಾರ್ಯಗಳನ್ನು ನಿರ್ವಹಿಸಲು ದಯವಿಟ್ಟು GPS ಸક્રિયಗೊಳಿಸಿ।",
        "retry": "ಈಗಲೇ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ",
        "online_users": "ಆನ್‌ಲೈನ್ ಬಳಕೆದಾರರು",
        "registered_users": "ನೋಂದಾಯಿತ ಬಳಕೆದಾರರು",
        "issues_resolved": "ಪರಿಹರಿಸಲಾದ ಸಮಸ್ಯೆಗಳು",
        "cities": "ನಗರಗಳು"
    },
    "ks": {
        "gps_disabled": "لوکیشن سروسز چھِ نااہل۔ مہروبٲنی کٔرتھ کٔریو اقدامات کرنہٕ خٲطرٕ GPS آن।",
        "retry": "دوبارہ کٔریو کوٗشش",
        "online_users": "آن لائن صارفین",
        "registered_users": "رجسٹرڈ صارفین",
        "issues_resolved": "حل گومتہِ مسائل",
        "cities": "شہر"
    },
    "ml": {
        "gps_disabled": "ലൊക്കേഷൻ സേവനങ്ങൾ പ്രവർത്തനരഹിതമാണ്. നടപടികൾ സ്വീകരിക്കാൻ ദയവായി GPS പ്രവർത്തനക്ഷമമാക്കുക।",
        "retry": "ഇപ്പോൾ വീണ്ടും ശ്രമിക്കുക",
        "online_users": "ഓൺലൈൻ ഉപയോക്താക്കൾ",
        "registered_users": "രജിസ്റ്റർ ചെയ്ത ഉപയോക്താക്കൾ",
        "issues_resolved": "പരിഹരിച്ച പ്രശ്നങ്ങൾ",
        "cities": "നഗരങ്ങൾ"
    },
    "mr": {
        "gps_disabled": "स्थान सेवा अक्षम आहेत. कृपया कृती करण्यासाठी GPS सक्षम करा।",
        "retry": "आत्ता पुन्हा प्रयत्न करा",
        "online_users": "ऑनलाइन वापरकर्ते",
        "registered_users": "नोंદણીકૃત वापरकर्તે",
        "issues_resolved": "सुटलेल्या समस्या",
        "cities": "શहरे"
    },
    "or": {
        "gps_disabled": "ଲୋକେସନ୍ ସେବା ଅକ୍ଷମ ଅଛି | କାର୍ଯ୍ୟ କରିବାକୁ ଦୟାକରି GPS ସକ୍ଷମ କରନ୍ତୁ |",
        "retry": "ବର୍ତ୍તମାନ ପୁନର୍ବାର ଚେଷ୍ଟା କରନ୍ତୁ",
        "online_users": "ଅନଲାଇନ୍ ବ୍ୟବହାରକାରୀ",
        "registered_users": "ପଞ୍ਜੀକୃତ ବ୍ୟବହାରକାରି",
        "issues_resolved": "ସମାଧାନ ହୋଇଥିବା ସମସ୍ୟା",
        "cities": "ସହרଗୁଡିକ"
    },
    "pa": {
        "gps_disabled": "ਲੋਕੇਸ਼ਨ ਸੇਵਾਵਾਂ ਅਯੋਗ ਹਨ। ਕਿਰਪา ਕਰਕੇ ਕਾਰਵਾਈ ਕਰਨ ਲਈ GPS ਨੂੰ ਚਾਲੂ ਕਰੋ।",
        "retry": "ਹੁਣੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ",
        "online_users": "ਔਨਲਾਈਨ ਉਪਭੋਗਤਾ",
        "registered_users": "ਰਜਿਸਟਰਡ ਉਪਭੋਗਤਾ",
        "issues_resolved": "ਹੱਲ ਕੀਤੇ ਮੁੱਦੇ",
        "cities": "ਸ਼ਹਿર"
    },
    "sa": {
        "gps_disabled": "स्थानसेवाः निष्क्रियाः सन्ति। कृपया कार्याणि कर्तुं GPS सक्रियं कुर्वन्तु।",
        "retry": "अधुनैव पुनः प्रयतस्व",
        "online_users": "ऑनलाइन-प्रयोक्तारः",
        "registered_users": "पञ्जीकृताः प्रयोक्तारः",
        "issues_resolved": "समाहिताः समस्याः",
        "cities": "नगराणि"
    },
    "sd": {
        "gps_disabled": "لوڪيشن سروسز غير فعال آهن. مهرباني ڪري عمل ڪرڻ لاءِ GPS کي فعال ڪريو.",
        "retry": "هاڻي ٻيهر ڪوشش ڪريو",
        "online_users": "آن لائن استعمال ڪندڙ",
        "registered_users": "رجسٽرڊ استعمال ڪندڙ",
        "issues_resolved": "حل ٿيل مسئلا",
        "cities": "شهر"
    },
    "ta": {
        "gps_disabled": "இருப்பிடச் சேவைகள் முடக்கப்பட்டுள்ளன. செயல்களைச் செய்ய தயவுசெய்து GPS-ஐ இயக்கவும்।",
        "retry": "இப்பொழுதே மீண்டும் முயற்சிக்கவும்",
        "online_users": "ஆன்லைன் பயனர்கள்",
        "registered_users": "பதிவு செய்யப்பட்ட பயனர்கள்",
        "issues_resolved": "தீர்க்கப்பட்ட சிக்கல்கள்",
        "cities": "நகரங்கள்"
    },
    "te": {
        "gps_disabled": "స్థాన సేవలు నిలిపివేయబడ్డాయి. చర్యలను నిర్వహించడానికి దయచేసి GPSని ప్రారంభించండి।",
        "retry": "ఇప్పుడే మళ్ళీ ప్రయత్నించండి",
        "online_users": "ఆన్‌లైన్ వినియోగదారులు",
        "registered_users": "నમોదిత వినియోగదారులు",
        "issues_resolved": "పరిష్కరించబడిన సమస్యలు",
        "cities": "నగరాలు"
    },
    "ur": {
        "gps_disabled": "لوکیشن سروسز غیر فعال ہیں۔ براہ کرم اقدامات کرنے کے لیے GPS فعال کریں۔",
        "retry": "ابھی دوبارہ کوشش کریں",
        "online_users": "آن لائن صارفین",
        "registered_users": "رجسٹرڈ صارفین",
        "issues_resolved": "حل شدہ مسائل",
        "cities": "شہر"
    }
}

for lang, data in translations.items():
    file_path = f"flask_app/app/translations/{lang}/LC_MESSAGES/messages.po"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Regex to find empty or fuzzy msgstr for specific msgids
        replacements = [
            (r'#, fuzzy\s*(msgid "Online Users")', r'\1'),
            (r'#, fuzzy\s*(msgid "Registered Users")', r'\1'),
            (r'#, fuzzy\s*(msgid "Issues Resolved")', r'\1'),
            (r'#, fuzzy\s*(msgid "Cities")', r'\1'),
            (r'(msgid "Location services are disabled\. Please enable GPS to perform actions\.")\s*msgstr ""', rf'\1\nmsgstr "{data["gps_disabled"]}"'),
            (r'(msgid "Retry Now")\s*msgstr ""', rf'\1\nmsgstr "{data["retry"]}"'),
            (r'(msgid "Online Users")\s*msgstr ""', rf'\1\nmsgstr "{data["online_users"]}"'),
            (r'(msgid "Registered Users")\s*msgstr ""', rf'\1\nmsgstr "{data["registered_users"]}"'),
            (r'(msgid "Issues Resolved")\s*msgstr ""', rf'\1\nmsgstr "{data["issues_resolved"]}"'),
            (r'(msgid "Cities")\s*msgstr ""', rf'\1\nmsgstr "{data["cities"]}"')
        ]

        new_content = content
        for pattern, replacement in replacements:
            p = re.compile(pattern)
            new_content = p.sub(replacement, new_content)

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"Updated {lang}")
        else:
            print(f"No change for {lang} (maybe already translated or pattern not found)")
    else:
        print(f"File not found: {file_path}")
