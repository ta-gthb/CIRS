$translations = @{
    "as" = @("স্থান সেৱা নিষ্ক্ৰিয় হৈ আছে। অনুগ্ৰহ কৰি কাৰ্য্য সম্পাদন কৰিবলৈ GPS সক্ষম কৰক।", "এতিয়াই পুনৰ চেষ্টা কৰক")
    "bn" = @("লোকেশন পরিষেবা নিষ্ক্রিয়। পদক্ষেপ নিতে দয়া করে GPS সক্ষম করুন।", "এখনই আবার চেষ্টা করুন")
    "gu" = @("સ્થાન સેવાઓ અક્ષમ છે. કૃપા કરીને ક્રિયાઓ કરવા માટે GPS સક્ષમ કરો।", "હમણાં ફરી પ્રયાસ કરો")
    "hi" = @("लोकेशन सेवाएं अक्षम हैं। कृपया कार्रवाई करने के लिए GPS सक्षम करें।", "अभी पुन: प्रयास करें")
    "kn" = @("ಸ್ಥಳ ಸೇವೆಗಳನ್ನು ನಿಷ್ಕ್ರಿಯಗೊಳಿಸಲಾಗಿದೆ. ಕಾರ್ಯಗಳನ್ನು ನಿರ್ವಹಿಸಲು ದಯವಿಟ್ಟು GPS ಸಕ್ರಿಯಗೊಳಿಸಿ।", "ಈಗಲೇ ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ")
    "ks" = @("لوکیشن سروسز چھِ نااہل۔ مہروبٲنی کٔرتھ کٔریو اقدامات کرنہٕ خٲطرٕ GPS آن۔", "دوبارہ کٔریو کوٗشش")
    "ml" = @("ലൊക്കേഷൻ സേവനങ്ങൾ പ്രവർത്തനരহিতമാണ്. നടപടികൾ സ്വീകരിക്കാൻ ദയവായി GPS പ്രവർത്തനക്ഷമമാക്കുക।", "ഇപ്പോൾ വീണ്ടും ശ്രമിക്കുക")
    "mr" = @("स्थान सेवा अक्षम आहेत. कृपया कृती करण्यासाठी GPS सक्षम करा।", "आत्ता पुन्हा प्रयत्न करा")
    "or" = @("ଲୋକେସନ୍ ସେବା ଅକ୍ଷମ ଅଛି | କାର୍ଯ୍ୟ କରିବାକୁ ଦୟାକରି GPS ସକ୍ଷମ କରନ୍ତୁ |", "ବର୍ତ୍ତମାନ ପୁନର୍ବାର ଚେଷ୍ଟା କରନ୍ତୁ")
    "pa" = @("ਲੋਕੇਸ਼ਨ ਸੇਵਾਵਾਂ ਅਯੋਗ ਹਨ। ਕਿਰਪਾ ਕਰਕੇ ਕਾਰਵਾਈ ਕਰਨ ਲਈ GPS ਨੂੰ ਚਾਲੂ ਕਰੋ।", "ਹੁਣੇ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ")
    "sa" = @("स्थानसेवाः निष्क्रियाः सन्ति। कृपया कार्याणि कर्तुं GPS सक्रियं कुर्वन्तु।", "अधुनैव पुनः प्रयतस्व")
    "sd" = @("لوڪيشن سروسز غير فعال آهن. مهرباني ڪري عمل ڪرڻ لاءِ GPS کي فعال ڪريو.", "هاڻي ٻيهر ڪوشش ڪريو")
    "ta" = @("இருப்பிடச் சேவைகள் முடக்கப்பட்டுள்ளன. செயல்களைச் செய்ய தயவுசெய்து GPS-ஐ இயக்கவும்।", "இப்பொழுதே மீண்டும் முயற்சிக்கவும்")
    "te" = @("స్థాన సేవలు నిలిపివేయబడ్డాయి. చర్యలను నిర్వహించడానికి దయచేసి GPSని ప్రారంభించండి।", "ఇప్పుడే మళ్ళీ ప్రయత్నించండి")
    "ur" = @("لوکیشن سروسز غیر فعال ہیں۔ براہ کرم اقدامات کرنے کے لیے GPS فعال کریں۔", "ابھی دوبارہ کوشش کریں")
}

foreach ($lang in $translations.Keys) {
    $file = "flask_app/app/translations/$lang/LC_MESSAGES/messages.po"
    if (Test-Path $file) {
        $t1 = $translations[$lang][0]
        $t2 = $translations[$lang][1]
        
        $content = Get-Content $file -Raw -Encoding UTF8
        
        # Escape backslashes and quotes for replacement string if any (though here we don't have much)
        # But we need to be careful with the regex
        
        $p1 = [regex]::Escape('msgid "Location services are disabled. Please enable GPS to perform actions."') + '\s*msgstr ""'
        $r1 = 'msgid "Location services are disabled. Please enable GPS to perform actions."`nmsgstr "' + $t1 + '"'
        
        $p2 = [regex]::Escape('msgid "Retry Now"') + '\s*msgstr ""'
        $r2 = 'msgid "Retry Now"`nmsgstr "' + $t2 + '"'
        
        $content = $content -replace $p1, $r1
        $content = $content -replace $p2, $r2
        
        Set-Content -Path $file -Value $content -Encoding UTF8
        Write-Host "Updated $lang"
    } else {
        Write-Host "File not found: $file"
    }
}
