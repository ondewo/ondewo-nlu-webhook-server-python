from enum import Enum
from functools import lru_cache
from typing import (
    Any,
    Dict,
    List,
    NewType,
    Optional,
    Set,
)

from langcodes import Language
from ondewo.logging.logger import logger_console as log

from ondewo_nlu_webhook_server.custom_exceptions import NotALanguageError

LOCALES_DICT: Dict[str, str] = {
    'multi': 'en_US.utf8',
    'aa_DJ': 'aa_DJ.utf8',  # Afar (Djibouti)
    'aa_ER': 'aa_ER.utf8',  # Afar (Eritrea)
    'aa_ER@saaho': 'aa_ER@saaho.utf8',  # Afar (Eritrea, Saaho)
    'aa_ET': 'aa_ET.utf8',  # Afar (Ethiopia)
    'ab_GE': 'ab_GE.utf8',  # Abkhaz (Georgia)
    'ae_AF': 'ae_AF.utf8',  # Avestan (Afghanistan)
    'af_ZA': 'af_ZA.utf8',  # Afrikaans (South Africa)
    'agr_PE': 'agr_PE.utf8',  # Aguaruna (Peru)
    'ak_GH': 'ak_GH.utf8',  # Akan (Ghana)
    'am_ET': 'am_ET.utf8',  # Amharic (Ethiopia)
    'an_ES': 'an_ES.utf8',  # Aragonese (Spain)
    'anp_IN': 'anp_IN.utf8',  # Angika (India)
    'ar_AE': 'ar_AE.utf8',  # Arabic (United Arab Emirates)
    'ar_BH': 'ar_BH.utf8',  # Arabic (Bahrain)
    'ar_DZ': 'ar_DZ.utf8',  # Arabic (Algeria)
    'ar_EG': 'ar_EG.utf8',  # Arabic (Egypt)
    'ar_IN': 'ar_IN.utf8',  # Arabic (India)
    'ar_IQ': 'ar_IQ.utf8',  # Arabic (Iraq)
    'ar_JO': 'ar_JO.utf8',  # Arabic (Jordan)
    'ar_KW': 'ar_KW.utf8',  # Arabic (Kuwait)
    'ar_LB': 'ar_LB.utf8',  # Arabic (Lebanon)
    'ar_LY': 'ar_LY.utf8',  # Arabic (Libya)
    'ar_MA': 'ar_MA.utf8',  # Arabic (Morocco)
    'ar_OM': 'ar_OM.utf8',  # Arabic (Oman)
    'ar_QA': 'ar_QA.utf8',  # Arabic (Qatar)
    'ar_SA': 'ar_SA.utf8',  # Arabic (Saudi Arabia)
    'ar_SD': 'ar_SD.utf8',  # Arabic (Sudan)
    'ar_SS': 'ar_SS.utf8',  # Arabic (South Sudan)
    'ar_SY': 'ar_SY.utf8',  # Arabic (Syria)
    'ar_TN': 'ar_TN.utf8',  # Arabic (Tunisia)
    'ar_YE': 'ar_YE.utf8',  # Arabic (Yemen)
    'ayc_PE': 'ayc_PE.utf8',  # Ayacucho Quechua (Peru)
    'az_AZ': 'az_AZ.utf8',  # Azerbaijani (Azerbaijan)
    'az_IR': 'az_IR.utf8',  # Azerbaijani (Iran)
    'as_IN': 'as_IN.utf8',  # Assamese (India)
    'ast_ES': 'ast_ES.utf8',  # Asturian (Spain)
    'be_BY': 'be_BY.utf8',  # Belarusian (Belarus)
    'be_BY@latin': 'be_BY@latin.utf8',  # Belarusian (Latin script)
    'bem_ZM': 'bem_ZM.utf8',  # Bemba (Zambia)
    'ber_DZ': 'ber_DZ.utf8',  # Berber (Algeria)
    'ber_MA': 'ber_MA.utf8',  # Berber (Morocco)
    'bg_BG': 'bg_BG.utf8',  # Bulgarian (Bulgaria)
    'bhb_IN': 'bhb_IN.utf8',  # Bhojpuri (India)
    'bho_IN': 'bho_IN.utf8',  # Bhojpuri (India)
    'bho_NP': 'bho_NP.utf8',  # Bhojpuri (Nepal)
    'bi_VU': 'bi_VU.utf8',  # Bislama (Vanuatu)
    'bn_BD': 'bn_BD.utf8',  # Bengali (Bangladesh)
    'bn_IN': 'bn_IN.utf8',  # Bengali (India)
    'bo_CN': 'bo_CN.utf8',  # Tibetan (China)
    'bo_IN': 'bo_IN.utf8',  # Tibetan (India)
    'br_FR': 'br_FR.utf8',  # Breton (France)
    'brx_IN': 'brx_IN.utf8',  # Bodo (India)
    'bs_BA': 'bs_BA.utf8',  # Bosnian (Bosnia and Herzegovina)
    'byn_ER': 'byn_ER.utf8',  # Blin (Eritrea)
    'C.UTF-8': 'C.UTF-8',  # C locale
    'ca_AD': 'ca_AD.utf8',  # Catalan (Andorra)
    'ca_ES': 'ca_ES.utf8',  # Catalan (Spain)
    'ca_ES@valencia': 'ca_ES@valencia.utf8',  # Catalan (Valencia)
    'ca_FR': 'ca_FR.utf8',  # Catalan (France)
    'ca_IT': 'ca_IT.utf8',  # Catalan (Italy)
    'ce_RU': 'ce_RU.utf8',  # Chechen (Russia)
    'chr_US': 'chr_US.utf8',  # Cherokee (United States)
    'ckb_IQ': 'ckb_IQ.utf8',  # Sorani Kurdish (Iraq)
    'cmn_TW': 'cmn_TW.utf8',  # Mandarin (Taiwan)
    'crh_UA': 'crh_UA.utf8',  # Crimean Tatar (Ukraine)
    'cs_CZ': 'cs_CZ.utf8',  # Czech (Czech Republic)
    'cv_RU': 'cv_RU.utf8',  # Chuvash (Russia)
    'cy_GB': 'cy_GB.utf8',  # Welsh (United Kingdom)
    'da_DK': 'da_DK.utf8',  # Danish (Denmark)
    'de_AT': 'de_AT.utf8',  # German (Austria)
    'de_BE': 'de_BE.utf8',  # German (Belgium)
    'de_CH': 'de_CH.utf8',  # German (Switzerland)
    'de_DE': 'de_DE.utf8',  # German (Germany)
    'de_IT': 'de_IT.utf8',  # German (Italy)
    'de_LI': 'de_LI.utf8',  # German (Liechtenstein)
    'de_LU': 'de_LU.utf8',  # German (Luxembourg)
    'doi_IN': 'doi_IN.utf8',  # Dogri (India)
    'dsb_DE': 'dsb_DE.utf8',  # Lower Sorbian (Germany)
    'dv_MV': 'dv_MV.utf8',  # Divehi (Maldives)
    'dz_BT': 'dz_BT.utf8',  # Dzongkha (Bhutan)
    'el_GR': 'el_GR.utf8',  # Greek (Greece)
    'el_CY': 'el_CY.utf8',  # Greek (Cyprus)
    'en_AG': 'en_AG.utf8',  # English (Antigua and Barbuda)
    'en_AU': 'en_AU.utf8',  # English (Australia)
    'en_BW': 'en_BW.utf8',  # English (Botswana)
    'en_CA': 'en_CA.utf8',  # English (Canada)
    'en_DK': 'en_DK.utf8',  # English (Denmark)
    'en_GB': 'en_GB.utf8',  # English (United Kingdom)
    'en_HK': 'en_HK.utf8',  # English (Hong Kong)
    'en_IE': 'en_IE.utf8',  # English (Ireland)
    'en_IL': 'en_IL.utf8',  # English (Israel)
    'en_IN': 'en_IN.utf8',  # English (India)
    'en_NG': 'en_NG.utf8',  # English (Nigeria)
    'en_NZ': 'en_NZ.utf8',  # English (New Zealand)
    'en_PH': 'en_PH.utf8',  # English (Philippines)
    'en_SG': 'en_SG.utf8',  # English (Singapore)
    'en_US': 'en_US.utf8',  # English (United States)
    'en_ZA': 'en_ZA.utf8',  # English (South Africa)
    'eo': 'eo.utf8',  # Esperanto
    'es_AR': 'es_AR.utf8',  # Spanish (Argentina)
    'es_BO': 'es_BO.utf8',  # Spanish (Bolivia)
    'es_CL': 'es_CL.utf8',  # Spanish (Chile)
    'es_CO': 'es_CO.utf8',  # Spanish (Colombia)
    'es_CR': 'es_CR.utf8',  # Spanish (Costa Rica)
    'es_DO': 'es_DO.utf8',  # Spanish (Dominican Republic)
    'es_EC': 'es_EC.utf8',  # Spanish (Ecuador)
    'es_ES': 'es_ES.utf8',  # Spanish (Spain)
    'es_GT': 'es_GT.utf8',  # Spanish (Guatemala)
    'es_HN': 'es_HN.utf8',  # Spanish (Honduras)
    'es_MX': 'es_MX.utf8',  # Spanish (Mexico)
    'es_NI': 'es_NI.utf8',  # Spanish (Nicaragua)
    'es_PA': 'es_PA.utf8',  # Spanish (Panama)
    'es_PY': 'es_PY.utf8',  # Spanish (Paraguay)
    'es_SV': 'es_SV.utf8',  # Spanish (El Salvador)
    'es_US': 'es_US.utf8',  # Spanish (United States)
    'es_UY': 'es_UY.utf8',  # Spanish (Uruguay)
    'es_VE': 'es_VE.utf8',  # Spanish (Venezuela)
    'et_EE': 'et_EE.utf8',  # Estonian (Estonia)
    'eu_ES': 'eu_ES.utf8',  # Basque (Spain)
    'fa_AF': 'fa_AF.utf8',  # Persian (Afghanistan)
    'fa_IR': 'fa_IR.utf8',  # Persian (Iran)
    'fi_FI': 'fi_FI.utf8',  # Finnish (Finland)
    'fil_PH': 'fil_PH.utf8',  # Filipino (Philippines)
    'fj_FJ': 'fj_FJ.utf8',  # Fijian (Fiji)
    'fo_FO': 'fo_FO.utf8',  # Faroese (Faroe Islands)
    'fr_BE': 'fr_BE.utf8',  # French (Belgium)
    'fr_CA': 'fr_CA.utf8',  # French (Canada)
    'fr_CH': 'fr_CH.utf8',  # French (Switzerland)
    'fr_FR': 'fr_FR.utf8',  # French (France)
    'fr_LU': 'fr_LU.utf8',  # French (Luxembourg)
    'fr_MC': 'fr_MC.utf8',  # French (Monaco)
    'fr_RE': 'fr_RE.utf8',  # French (Réunion)
    'ga_IE': 'ga_IE.utf8',  # Irish (Ireland)
    'gd_GB': 'gd_GB.utf8',  # Scottish Gaelic (United Kingdom)
    'gl_ES': 'gl_ES.utf8',  # Galician (Spain)
    'gn_PY': 'gn_PY.utf8',  # Guarani (Paraguay)
    'gu_IN': 'gu_IN.utf8',  # Gujarati (India)
    'gux_PE': 'gux_PE.utf8',  # Aguaruna (Peru)
    'ha_NG': 'ha_NG.utf8',  # Hausa (Nigeria)
    'hak_TW': 'hak_TW.utf8',  # Hakka (Taiwan)
    'he_IL': 'he_IL.utf8',  # Hebrew (Israel)
    'hi_IN': 'hi_IN.utf8',  # Hindi (India)
    'hr_HR': 'hr_HR.utf8',  # Croatian (Croatia)
    'hsb_DE': 'hsb_DE.utf8',  # Upper Sorbian (Germany)
    'ht_HT': 'ht_HT.utf8',  # Haitian Creole (Haiti)
    'hu_HU': 'hu_HU.utf8',  # Hungarian (Hungary)
    'hy_AM': 'hy_AM.utf8',  # Armenian (Armenia)
    'ia': 'ia.utf8',  # Interlingua
    'id_ID': 'id_ID.utf8',  # Indonesian (Indonesia)
    'ig_NG': 'ig_NG.utf8',  # Igbo (Nigeria)
    'ii_CN': 'ii_CN.utf8',  # Yi (China)
    'is_IS': 'is_IS.utf8',  # Icelandic (Iceland)
    'it_CH': 'it_CH.utf8',  # Italian (Switzerland)
    'it_IT': 'it_IT.utf8',  # Italian (Italy)
    'ja_JP': 'ja_JP.utf8',  # Japanese (Japan)
    'jv_ID': 'jv_ID.utf8',  # Javanese (Indonesia)
    'ka_GE': 'ka_GE.utf8',  # Georgian (Georgia)
    'kab_DZ': 'kab_DZ.utf8',  # Kabyle (Algeria)
    'kac_MM': 'kac_MM.utf8',  # Kachin (Myanmar)
    'kbd_RU': 'kbd_RU.utf8',  # Kabardian (Russia)
    'kha_IN': 'kha_IN.utf8',  # Khasi (India)
    'khm_KH': 'khm_KH.utf8',  # Khmer (Cambodia)
    'ki_KE': 'ki_KE.utf8',  # Kikuyu (Kenya)
    'kj_AO': 'kj_AO.utf8',  # Kuanyama (Angola)
    'kk_KZ': 'kk_KZ.utf8',  # Kazakh (Kazakhstan)
    'kl_GL': 'kl_GL.utf8',  # Greenlandic (Greenland)
    'km_KH': 'km_KH.utf8',  # Khmer (Cambodia)
    'kn_IN': 'kn_IN.utf8',  # Kannada (India)
    'ko_KR': 'ko_KR.utf8',  # Korean (South Korea)
    'kri_LR': 'kri_LR.utf8',  # Krio (Liberia)
    'ku_TR': 'ku_TR.utf8',  # Kurdish (Turkey)
    'ku_IQ': 'ku_IQ.utf8',  # Kurdish (Iraq)
    'ku_SY': 'ku_SY.utf8',  # Kurdish (Syria)
    'la': 'la.utf8',  # Latin
    'lb_LU': 'lb_LU.utf8',  # Luxembourgish (Luxembourg)
    'lg_UG': 'lg_UG.utf8',  # Ganda (Uganda)
    'li_NL': 'li_NL.utf8',  # Limburgish (Netherlands)
    'ln_CD': 'ln_CD.utf8',  # Lingala (Democratic Republic of the Congo)
    'lo_LA': 'lo_LA.utf8',  # Lao (Laos)
    'lt_LT': 'lt_LT.utf8',  # Lithuanian (Lithuania)
    'lv_LV': 'lv_LV.utf8',  # Latvian (Latvia)
    'mg_MG': 'mg_MG.utf8',  # Malagasy (Madagascar)
    'mi_NZ': 'mi_NZ.utf8',  # Māori (New Zealand)
    'mk_MK': 'mk_MK.utf8',  # Macedonian (North Macedonia)
    'ml_IN': 'ml_IN.utf8',  # Malayalam (India)
    'mn_MN': 'mn_MN.utf8',  # Mongolian (Mongolia)
    'mo_RO': 'mo_RO.utf8',  # Moldovan (Romania)
    'mr_IN': 'mr_IN.utf8',  # Marathi (India)
    'ms_MY': 'ms_MY.utf8',  # Malay (Malaysia)
    'mt_MT': 'mt_MT.utf8',  # Maltese (Malta)
    'my_MM': 'my_MM.utf8',  # Burmese (Myanmar)
    'na_NR': 'na_NR.utf8',  # Nauruan (Nauru)
    'nah_MX': 'nah_MX.utf8',  # Nahuatl (Mexico)
    'nb_NO': 'nb_NO.utf8',  # Norwegian (Bokmål, Norway)
    'nd_ZW': 'nd_ZW.utf8',  # Northern Ndebele (Zimbabwe)
    'ne_NP': 'ne_NP.utf8',  # Nepali (Nepal)
    'nl_BE': 'nl_BE.utf8',  # Dutch (Belgium)
    'nl_NL': 'nl_NL.utf8',  # Dutch (Netherlands)
    'nn_NO': 'nn_NO.utf8',  # Norwegian (Nynorsk, Norway)
    'no_NO': 'no_NO.utf8',  # Norwegian (Norway)
    'nr_ZA': 'nr_ZA.utf8',  # Southern Ndebele (South Africa)
    'nso_ZA': 'nso_ZA.utf8',  # Northern Sotho (South Africa)
    'ny_MW': 'ny_MW.utf8',  # Chichewa (Malawi)
    'om_ET': 'om_ET.utf8',  # Oromo (Ethiopia)
    'or_IN': 'or_IN.utf8',  # Odia (India)
    'os_RU': 'os_RU.utf8',  # Ossetic (Russia)
    'pa_IN': 'pa_IN.utf8',  # Punjabi (India)
    'pa_PK': 'pa_PK.utf8',  # Punjabi (Pakistan)
    'pl_PL': 'pl_PL.utf8',  # Polish (Poland)
    'ps_AF': 'ps_AF.utf8',  # Pashto (Afghanistan)
    'pt_BR': 'pt_BR.utf8',  # Portuguese (Brazil)
    'pt_PT': 'pt_PT.utf8',  # Portuguese (Portugal)
    'quz_PE': 'quz_PE.utf8',  # Quechua (Peru)
    'rm_CH': 'rm_CH.utf8',  # Romansh (Switzerland)
    'rn_BI': 'rn_BI.utf8',  # Kirundi (Burundi)
    'ro_RO': 'ro_RO.utf8',  # Romanian (Romania)
    'ru_RU': 'ru_RU.utf8',  # Russian (Russia)
    'rw_RW': 'rw_RW.utf8',  # Kinyarwanda (Rwanda)
    'sa_IN': 'sa_IN.utf8',  # Sanskrit (India)
    'sc_IT': 'sc_IT.utf8',  # Sardinian (Italy)
    'sd_IN': 'sd_IN.utf8',  # Sindhi (India)
    'se_NO': 'se_NO.utf8',  # Northern Sami (Norway)
    'sg_CF': 'sg_CF.utf8',  # Sango (Central African Republic)
    'sh_BA': 'sh_BA.utf8',  # Serbo-Croatian (Bosnia and Herzegovina)
    'si_LK': 'si_LK.utf8',  # Sinhalese (Sri Lanka)
    'sk_SK': 'sk_SK.utf8',  # Slovak (Slovakia)
    'sl_SI': 'sl_SI.utf8',  # Slovenian (Slovenia)
    'sm_WS': 'sm_WS.utf8',  # Samoan (Samoa)
    'sn_ZW': 'sn_ZW.utf8',  # Shona (Zimbabwe)
    'so_SO': 'so_SO.utf8',  # Somali (Somalia)
    'sq_AL': 'sq_AL.utf8',  # Albanian (Albania)
    'sr_RS': 'sr_RS.utf8',  # Serbian (Serbia)
    'ss_ZA': 'ss_ZA.utf8',  # Swati (South Africa)
    'st_ZA': 'st_ZA.utf8',  # Southern Sotho (South Africa)
    'su_ID': 'su_ID.utf8',  # Sundanese (Indonesia)
    'sv_SE': 'sv_SE.utf8',  # Swedish (Sweden)
    'sw_TZ': 'sw_TZ.utf8',  # Swahili (Tanzania)
    'ta_IN': 'ta_IN.utf8',  # Tamil (India)
    'te_IN': 'te_IN.utf8',  # Telugu (India)
    'tg_TJ': 'tg_TJ.utf8',  # Tajik (Tajikistan)
    'th_TH': 'th_TH.utf8',  # Thai (Thailand)
    'ti_ER': 'ti_ER.utf8',  # Tigrinya (Eritrea)
    'tk_TM': 'tk_TM.utf8',  # Turkmen (Turkmenistan)
    'tl_PH': 'tl_PH.utf8',  # Tagalog (Philippines)
    'tn_ZA': 'tn_ZA.utf8',  # Tswana (South Africa)
    'to_TO': 'to_TO.utf8',  # Tongan (Tonga)
    'tr_TR': 'tr_TR.utf8',  # Turkish (Turkey)
    'ts_ZA': 'ts_ZA.utf8',  # Tsonga (South Africa)
    'tt_RU': 'tt_RU.utf8',  # Tatar (Russia)
    'ug_CN': 'ug_CN.utf8',  # Uyghur (China)
    'uk_UA': 'uk_UA.utf8',  # Ukrainian (Ukraine)
    'ur_PK': 'ur_PK.utf8',  # Urdu (Pakistan)
    'uz_UZ': 'uz_UZ.utf8',  # Uzbek (Uzbekistan)
    'vi_VN': 'vi_VN.utf8',  # Vietnamese (Vietnam)
    'wa_BE': 'wa_BE.utf8',  # Walloon (Belgium)
    'xh_ZA': 'xh_ZA.utf8',  # Xhosa (South Africa)
    'yi': 'yi.utf8',  # Yiddish
    'yo_NG': 'yo_NG.utf8',  # Yoruba (Nigeria)
    'za_CN': 'za_CN.utf8',  # Zhuang (China)
    'zu_ZA': 'zu_ZA.utf8',  # Zulu (South Africa)
}

LANGUAGE_TO_LOCALES_DICT: Dict[str, Set[str]] = {
    'multi': {'multi'},
    'af': {'af-ZA'},
    'am': {'am-ET'},
    'ar': {
        'ar-EG',
        'ar-KW',
        'ar-LB',
        'ar-MR',
        'ar-BH',
        'ar-DZ',
        'ar-TN',
        'ar-PS',
        'ar-SD',
        'ar-AE',
        'ar-SA',
        'ar-YE',
        'ar-MA',
        'ar-SY',
        'ar-LY',
        'ar-QA',
        'ar-OM',
        'ar-IL',
        'ar-IQ',
        'ar-JO',
    },
    'az': {'az-AZ'},
    'bg': {'bg-BG'},
    'bn': {
        'bn-IN',
        'bn-BD',
    },
    'bs': {'bs-BA'},
    'ca': {
        'ca-ES',
        'ca-IT',
        'ca-FR',
        'ca-AD',
    },
    'cmn': {
        'cmn-Hant-TW',
        'cmn-Hans-HK',
        'cmn-Hans-CN',
    },
    'cs': {'cs-CZ'},
    'ckb': {
        'ckb-IR',
        'ckb-IQ',
    },
    'cy': {'cy-GB'},
    'da': {
        'da-DK',
        'da-GL',
    },
    'de': {
        'de-AT',
        'de-DE',
        'de-BE',
        'de-LI',
        'de-CH',
        'de-LU',
    },
    'el': {
        'el-CY',
        'el-GR',
    },
    'en': {
        'en-SG',
        'en-PR',
        'en-NZ',
        'en-GM',
        'en-PH',
        'en-GB',
        'en-RW',
        'en-NI',
        'en-IO',
        'en-IN',
        'en-CA',
        'en-SC',
        'en-TT',
        'en-GY',
        'en-MK',
        'en-FI',
        'en-ZA',
        'en-BZ',
        'en-NR',
        'en-MO',
        'en-KE',
        'en-VG',
        'en-MT',
        'en-TZ',
        'en-TK',
        'en-BE',
        'en-IE',
        'en-NG',
        'en-SH',
        'en-GH',
        'en-HK',
        'en-BA',
        'en-MU',
        'en-US',
        'en-VI',
        'en-LC',
        'en-JE',
        'en-AU',
        'en-PK',
        'en-JM',
        'en-NF',
        'en-ZW',
        'en-BW',
        'en-AG',
    },
    'es': {
        'es-PY',
        'es-SV',
        'es-NI',
        'es-CV',
        'es-HN',
        'es-PE',
        'es-MX',
        'es-DO',
        'es-VE',
        'es-EC',
        'es-AR',
        'es-BO',
        'es-CR',
        'es-CL',
        'es-ES',
        'es-UY',
        'es-CO',
        'es-PA',
        'es-GT',
        'es-PR',
        'es-CU',
        'es-US',
    },
    'et': {'et-EE'},
    'eu': {'eu-ES'},
    'fa': {'fa-IR'},
    'fi': {'fi-FI'},
    'fil': {
        'fil-PH',
        'tl-PH',
    },
    'fr': {
        'fr-HT',
        'fr-CI',
        'fr-MA',
        'fr-FR',
        'fr-VN',
        'fr-BI',
        'fr-SN',
        'fr-RW',
        'fr-GA',
        'fr-SC',
        'fr-CG',
        'fr-NE',
        'fr-GN',
        'fr-LU',
        'fr-TG',
        'fr-DJ',
        'fr-DZ',
        'fr-MU',
        'fr-RE',
        'fr-MR',
        'fr-BE',
        'fr-TD',
        'fr-CD',
        'fr-CF',
        'fr-CH',
        'fr-CA',
    },
    'gl': {'gl-ES'},
    'gu': {'gu-IN'},
    'he': {
        'he-IL',
        'iw-IL',
    },
    'hi': {'hi-IN'},
    'hr': {'hr-HR'},
    'hu': {'hu-HU'},
    'hy': {'hy-AM'},
    'id': {'id-ID'},
    'is': {'is-IS'},
    'it': {
        'it-IT',
        'it-CH',
        'it-VA',
        'it-SM',
    },
    'ja': {'ja-JP'},
    'jv': {
        'jv-ID',
        'jw-ID',
    },
    'ka': {'ka-GE'},
    'kk': {'kk-KZ'},
    'km': {'km-KH'},
    'kn': {'kn-IN'},
    'ko': {'ko-KR'},
    'ku': {'ku-TR'},
    'ky': {'ky-KG'},
    'la': {'la-VA'},
    'lb': {'lb-LU'},
    'lo': {'lo-LA'},
    'lt': {'lt-LT'},
    'lv': {'lv-LV'},
    'mi': {'mi-NZ'},
    'mk': {'mk-MK'},
    'ml': {'ml-IN'},
    'mn': {'mn-MN'},
    'mr': {'mr-IN'},
    'ms': {'ms-MY'},
    'mt': {'mt-MT'},
    'my': {'my-MM'},
    'ne': {'ne-NP'},
    'nl': {
        'nl-NL',
        'nl-BE',
    },
    'no': {'no-NO'},
    'ps': {'ps-AF'},
    'pa': {
        'pa-IN',
        'pa-PK',
        'pa-Guru-IN',
    },
    'pl': {'pl-PL'},
    'pt': {
        'pt-MZ',
        'pt-PT',
        'pt-TL',
        'pt-GW',
        'pt-CV',
        'pt-AO',
        'pt-MO',
        'pt-BR',
    },
    'ro': {
        'ro-MD',
        'ro-RO',
    },
    'ru': {
        'ru-KZ',
        'ru-RU',
        'ru-BY',
    },
    'rw': {'rw-RW'},
    'si': {'si-LK'},
    'sk': {'sk-SK'},
    'sl': {'sl-SI'},
    'so': {
        'so-UG',
        'so-KE',
        'so-DJ',
        'so-SO',
        'so-ET',
    },
    'sq': {'sq-AL'},
    'sr': {
        'sr-BA',
        'sr-CY',
        'sr-RS',
    },
    'ss': {'ss-Latn-ZA'},
    'st': {'st-ZA'},
    'su': {'su-ID'},
    'sv': {
        'sv-FI',
        'sv-SE',
    },
    'sw': {
        'sw-TZ',
        'sw-KE',
    },
    'ta': {
        'ta-MY',
        'ta-SG',
        'ta-IN',
        'ta-LK',
    },
    'te': {'te-IN'},
    'th': {'th-TH'},
    'tn': {'tn-Latn-ZA'},
    'tr': {'tr-TR'},
    'ts': {'ts-ZA'},
    'uk': {'uk-UA'},
    'ur': {
        'ur-PK',
        'ur-IN',
    },
    'uz': {'uz-UZ'},
    've': {'ve-ZA'},
    'vi': {'vi-VN'},
    'xh': {'xh-ZA'},
    'yi': {'yi-US'},
    'yue': {'yue-Hant-HK'},
    'zh': {
        'zh-CN',
        'zh-SG',
        'zh-TW',
        'zh-HK',
    },
    'zu': {'zu-ZA'},
}


class LanguageCode(Enum):
    multi = "multi"  # Multi language fallback
    af_ZA = "af-ZA"  # Afrikaans (South Africa)
    am_ET = "am-ET"  # Amharic (Ethiopia)
    ar_AE = "ar-AE"  # Arabic (United Arab Emirates)
    ar_BH = "ar-BH"  # Arabic (Bahrain)
    ar_DZ = "ar-DZ"  # Arabic (Algeria)
    ar_EG = "ar-EG"  # Arabic (Egypt)
    ar_IL = "ar-IL"  # Arabic (Israel)
    ar_IQ = "ar-IQ"  # Arabic (Iraq)
    ar_JO = "ar-JO"  # Arabic (Jordan)
    ar_KW = "ar-KW"  # Arabic (Kuwait)
    ar_LB = "ar-LB"  # Arabic (Lebanon)
    ar_LY = "ar-LY"  # Arabic (Libya)
    ar_MA = "ar-MA"  # Arabic (Morocco)
    ar_MR = "ar-MR"  # Arabic (Mauritania)
    ar_OM = "ar-OM"  # Arabic (Oman)
    ar_PS = "ar-PS"  # Arabic (State of Palestine)
    ar_QA = "ar-QA"  # Arabic (Qatar)
    ar_SA = "ar-SA"  # Arabic (Saudi Arabia)
    ar_SD = "ar-SD"  # Arabic (Sudan)
    ar_SY = "ar-SY"  # Arabic (Syria)
    ar_TN = "ar-TN"  # Arabic (Tunisia)
    ar_YE = "ar-YE"  # Arabic (Yemen)
    az_AZ = "az-AZ"  # Azerbaijani (Azerbaijan)
    bg_BG = "bg-BG"  # Bulgarian (Bulgaria)
    bn_BD = "bn-BD"  # Bengali (Bangladesh)
    bn_IN = "bn-IN"  # Bengali (India)
    bs_BA = "bs-BA"  # Bosnian (Bosnia and Herzegovina)
    ca_AD = "ca-AD"  # Catalan (Andorra)
    ca_ES = "ca-ES"  # Catalan (Spain)
    ca_FR = "ca-FR"  # Catalan (France)
    ca_IT = "ca-IT"  # Catalan (Italy)
    ckb_IR = "ckb-IR"  # Sorani (Iraq)
    ckb_IQ = "ckb-IQ"  # Central Kurdish(Iraq)
    cmn_Hans_CN = "cmn-Hans-CN"  # Chinese (Simplified, China)
    cmn_Hans_HK = "cmn-Hans-HK"  # Chinese (Simplified, Hong Kong)
    cmn_Hant_TW = "cmn-Hant-TW"  # Chinese (Traditional, Taiwan)
    cs_CZ = "cs-CZ"  # Czech (Czech Republic)
    cy_GB = "cy-GB"  # Welsh (United Kingdom)
    da_DK = "da-DK"  # Danish (Denmark)
    da_GL = "da-GL"  # Danish (Greenland)
    de_AT = "de-AT"  # German (Austria)
    de_BE = "de-BE"  # German (Belgium)
    de_CH = "de-CH"  # German (Switzerland)
    de_DE = "de-DE"  # German (Germany)
    de_LI = "de-LI"  # German (Liechtenstein)
    de_LU = "de-LU"  # German (Luxembourg)
    el_CY = "el-CY"  # Greek (Cyprus)
    el_GR = "el-GR"  # Greek (Greece)
    en_AG = "en-AG"  # English (Antigua and Barbuda)
    en_AU = "en-AU"  # English (Australia)
    en_BA = "en-BA"  # English (Bosnia and Herzegovina)
    en_BE = "en-BE"  # English (Belgium)
    en_BW = "en-BW"  # English (Botswana)
    en_BZ = "en-BZ"  # English (Belize)
    en_CA = "en-CA"  # English (Canada)
    en_FI = "en-FI"  # English (Finland)
    en_GB = "en-GB"  # English (United Kingdom)
    en_GH = "en-GH"  # English (Ghana)
    en_GM = "en-GM"  # English (Gambia)
    en_GY = "en-GY"  # English (Guyana)
    en_HK = "en-HK"  # English (Hong Kong)
    en_IE = "en-IE"  # English (Ireland)
    en_IN = "en-IN"  # English (India)
    en_IO = "en-IO"  # English (British Indian Ocean Territory)
    en_JE = "en-JE"  # English (Jersey)
    en_JM = "en-JM"  # English (Jamaica)
    en_KE = "en-KE"  # English (Kenya)
    en_LC = "en-LC"  # English (Saint Lucia)
    en_MK = "en-MK"  # English (North Macedonia)
    en_MO = "en-MO"  # English (Macau)
    en_MT = "en-MT"  # English (Malta)
    en_MU = "en-MU"  # English (Mauritius)
    en_NF = "en-NF"  # English (Norfolk Island)
    en_NG = "en-NG"  # English (Nigeria)
    en_NI = "en-NI"  # English (Nicaragua)
    en_NR = "en-NR"  # English (Nauru)
    en_NZ = "en-NZ"  # English (New Zealand)
    en_PH = "en-PH"  # English (Philippines)
    en_PK = "en-PK"  # English (Pakistan)
    en_PR = "en-PR"  # English (Puerto Rico)
    en_RW = "en-RW"  # English (Rwanda)
    en_SC = "en-SC"  # English (Seychelles)
    en_SG = "en-SG"  # English (Singapore)
    en_SH = "en-SH"  # English (Saint Helena)
    en_TK = "en-TK"  # English (Tokelau)
    en_TT = "en-TT"  # English (Trinidad and Tobago)
    en_TZ = "en-TZ"  # English (Tanzania)
    en_US = "en-US"  # English (United States)
    en_VG = "en-VG"  # English (British Virgin Islands)
    en_VI = "en-VI"  # English (U.S. Virgin Islands)
    en_ZA = "en-ZA"  # English (South Africa)
    en_ZW = "en-ZW"  # English (Zimbabwe)
    es_AR = "es-AR"  # Spanish (Argentina)
    es_BO = "es-BO"  # Spanish (Bolivia)
    es_CL = "es-CL"  # Spanish (Chile)
    es_CO = "es-CO"  # Spanish (Colombia)
    es_CR = "es-CR"  # Spanish (Costa Rica)
    es_CU = "es-CU"  # Spanish (Cuba)
    es_CV = "es-CV"  # Spanish (Cape Verde)
    es_DO = "es-DO"  # Spanish (Dominican Republic)
    es_EC = "es-EC"  # Spanish (Ecuador)
    es_ES = "es-ES"  # Spanish (Spain)
    es_GT = "es-GT"  # Spanish (Guatemala)
    es_HN = "es-HN"  # Spanish (Honduras)
    es_MX = "es-MX"  # Spanish (Mexico)
    es_NI = "es-NI"  # Spanish (Nicaragua)
    es_PA = "es-PA"  # Spanish (Panama)
    es_PE = "es-PE"  # Spanish (Peru)
    es_PR = "es-PR"  # Spanish (Puerto Rico)
    es_PY = "es-PY"  # Spanish (Paraguay)
    es_SV = "es-SV"  # Spanish (El Salvador)
    es_US = "es-US"  # Spanish (United States)
    es_UY = "es-UY"  # Spanish (Uruguay)
    es_VE = "es-VE"  # Spanish (Venezuela)
    et_EE = "et-EE"  # Estonian (Estonia)
    eu_ES = "eu-ES"  # Basque (Spain)
    fa_IR = "fa-IR"  # Persian (Iran)
    fi_FI = "fi-FI"  # Finnish (Finland)
    fil_PH = "fil-PH"  # Filipino (Philippines)
    fr_BE = "fr-BE"  # French (Belgium)
    fr_BI = "fr-BI"  # French (Burundi)
    fr_CA = "fr-CA"  # French (Canada)
    fr_CD = "fr-CD"  # French (Congo - Kinshasa)
    fr_CF = "fr-CF"  # French (Central African Republic)
    fr_CG = "fr-CG"  # French (Congo - Brazzaville)
    fr_CH = "fr-CH"  # French (Switzerland)
    fr_CI = "fr-CI"  # French (Ivory Coast)
    fr_DJ = "fr-DJ"  # French (Djibouti)
    fr_DZ = "fr-DZ"  # French (Algeria)
    fr_FR = "fr-FR"  # French (France)
    fr_GA = "fr-GA"  # French (Gabon)
    fr_GN = "fr-GN"  # French (Guinea)
    fr_HT = "fr-HT"  # French (Haiti)
    fr_LU = "fr-LU"  # French (Luxembourg)
    fr_MA = "fr-MA"  # French (Morocco)
    fr_MR = "fr-MR"  # French (Mauritania)
    fr_MU = "fr-MU"  # French (Mauritius)
    fr_NE = "fr-NE"  # French (Niger)
    fr_RE = "fr-RE"  # French (Réunion)
    fr_RW = "fr-RW"  # French (Rwanda)
    fr_SC = "fr-SC"  # French (Seychelles)
    fr_SN = "fr-SN"  # French (Senegal)
    fr_TD = "fr-TD"  # French (Chad)
    fr_TG = "fr-TG"  # French (Togo)
    fr_VN = "fr-VN"  # French (Vietnam)
    gl_ES = "gl-ES"  # Galician (Spain)
    gu_IN = "gu-IN"  # Gujarati (India)
    he_IL = "he-IL"  # Hebrew (Israel)
    hi_IN = "hi-IN"  # Hindi (India)
    hr_HR = "hr-HR"  # Croatian (Croatia)
    hu_HU = "hu-HU"  # Hungarian (Hungary)
    hy_AM = "hy-AM"  # Armenian (Armenia)
    id_ID = "id-ID"  # Indonesian (Indonesia)
    is_IS = "is-IS"  # Icelandic (Iceland)
    it_CH = "it-CH"  # Italian (Switzerland)
    it_IT = "it-IT"  # Italian (Italy)
    it_SM = "it-SM"  # Italian (San Marino)
    it_VA = "it-VA"  # Italian (Vatican City)
    iw_IL = "iw-IL"  # Hebrew (Israel)
    ja_JP = "ja-JP"  # Japanese (Japan)
    jv_ID = "jv-ID"  # Javanese (Indonesia)
    jw_ID = "jw-ID"  # Javanese (Indonesia)
    ka_GE = "ka-GE"  # Georgian (Georgia)
    kk_KZ = "kk-KZ"  # Kazakh (Kazakhstan)
    km_KH = "km-KH"  # Khmer (Cambodia)
    kn_IN = "kn-IN"  # Kannada (India)
    ko_KR = "ko-KR"  # Korean (South Korea)
    ku_TR = "ku-TR"  # Kurdish (Turkey)
    ky_KG = "ky-KG"  # Kyrgyz (Kyrgyzstan)
    la_VA = "la-VA"  # Latin (Vatican City)
    lb_LU = "lb-LU"  # Luxembourgish (Luxembourg)
    lo_LA = "lo-LA"  # Lao (Laos)
    lt_LT = "lt-LT"  # Lithuanian (Lithuania)
    lv_LV = "lv-LV"  # Latvian (Latvia)
    mi_NZ = "mi-NZ"  # Maori (New Zealand)
    mk_MK = "mk-MK"  # Macedonian (North Macedonia)
    ml_IN = "ml-IN"  # Malayalam (India)
    mn_MN = "mn-MN"  # Mongolian (Mongolia)
    mr_IN = "mr-IN"  # Marathi (India)
    ms_MY = "ms-MY"  # Malay (Malaysia)
    mt_MT = "mt-MT"  # Maltese (Malta)
    my_MM = "my-MM"  # Burmese (Myanmar)
    ne_NP = "ne-NP"  # Nepali (Nepal)
    nl_BE = "nl-BE"  # Dutch (Belgium)
    nl_NL = "nl-NL"  # Dutch (Netherlands)
    no_NO = "no-NO"  # Norwegian Bokmål (Norway)
    pa_Guru_IN = "pa-Guru-IN"  # Punjabi (Gurmukhi India)
    pa_IN = "pa-IN"  # Punjabi (India)
    pa_PK = "pa-PK"  # Punjabi (Pakistan)
    ps_AF = "ps-AF"  # Pashto / Paschtu (Afghanistan)
    pl_PL = "pl-PL"  # Polish (Poland)
    pt_AO = "pt-AO"  # Portuguese (Angola)
    pt_BR = "pt-BR"  # Portuguese (Brazil)
    pt_CV = "pt-CV"  # Portuguese (Cape Verde)
    pt_GW = "pt-GW"  # Portuguese (Guinea-Bissau)
    pt_MO = "pt-MO"  # Portuguese (Macau)
    pt_MZ = "pt-MZ"  # Portuguese (Mozambique)
    pt_PT = "pt-PT"  # Portuguese (Portugal)
    pt_TL = "pt-TL"  # Portuguese (Timor-Leste)
    ro_MD = "ro-MD"  # Romanian (Moldova)
    ro_RO = "ro-RO"  # Romanian (Romania)
    ru_BY = "ru-BY"  # Russian (Belarus)
    ru_KZ = "ru-KZ"  # Russian (Kazakhstan)
    ru_RU = "ru-RU"  # Russian (Russia)
    rw_RW = "rw-RW"  # Kinyarwanda (Rwanda)
    si_LK = "si-LK"  # Sinhala (Sri Lanka)
    sk_SK = "sk-SK"  # Slovak (Slovakia)
    sl_SI = "sl-SI"  # Slovenian (Slovenia)
    so_DJ = "so-DJ"  # Somali (Djibouti)
    so_ET = "so-ET"  # Somali (Ethiopia)
    so_KE = "so-KE"  # Somali (Kenya)
    so_SO = "so-SO"  # Somali (Somalia)
    so_UG = "so-UG"  # Somali (Uganda)
    sq_AL = "sq-AL"  # Albanian (Albania)
    sr_BA = "sr-BA"  # Serbian (Bosnia and Herzegovina)
    sr_CY = "sr-CY"  # Serbian (Cyprus)
    sr_RS = "sr-RS"  # Serbian (Serbia)
    ss_Latn_ZA = "ss-Latn-ZA"  # Swati (Latin, South Africa)
    st_ZA = "st-ZA"  # Southern Sotho (South Africa)
    su_ID = "su-ID"  # Sundanese (Indonesia)
    sv_FI = "sv-FI"  # Swedish (Finland)
    sv_SE = "sv-SE"  # Swedish (Sweden)
    sw_KE = "sw-KE"  # Swahili (Kenya)
    sw_TZ = "sw-TZ"  # Swahili (Tanzania)
    ta_IN = "ta-IN"  # Tamil (India)
    ta_LK = "ta-LK"  # Tamil (Sri Lanka)
    ta_MY = "ta-MY"  # Tamil (Malaysia)
    ta_SG = "ta-SG"  # Tamil (Singapore)
    te_IN = "te-IN"  # Telugu (India)
    th_TH = "th-TH"  # Thai (Thailand)
    tl_PH = "tl-PH"  # Filipino (Philippines)
    tn_Latn_ZA = "tn-Latn-ZA"  # Tswana (Latin, South Africa)
    tr_TR = "tr-TR"  # Turkish (Turkey)
    ts_ZA = "ts-ZA"  # Tsonga (South Africa)
    uk_UA = "uk-UA"  # Ukrainian (Ukraine)
    ur_IN = "ur-IN"  # Urdu (India)
    ur_PK = "ur-PK"  # Urdu (Pakistan)
    uz_UZ = "uz-UZ"  # Uzbek (Uzbekistan)
    ve_ZA = "ve-ZA"  # Venda (South Africa)
    vi_VN = "vi-VN"  # Vietnamese (Vietnam)
    xh_ZA = "xh-ZA"  # Xhosa (South Africa)
    yi_US = "yi-US"  # Yiddish (United States)
    yue_Hant_HK = "yue-Hant-HK"  # Chinese, Cantonese (Traditional Hong Kong)
    zh_CN = "zh-CN"  # Chinese (China)
    zh_HK = "zh-HK"  # Chinese (Hong Kong)
    zh_SG = "zh-SG"  # Chinese (Singapore)
    zh_TW = "zh-TW"  # Chinese (Taiwan)
    zu_ZA = "zu-ZA"  # Zulu (South Africa)

    ValueType = NewType('ValueType', str)

    @classmethod
    def _missing_(cls, value: object) -> Enum:
        if not isinstance(value, str):
            raise ValueError(f"Cannot instantiate '{cls.__name__}' from value '{value}'. Expect a string.")

        value_str: str = str(value)
        value_str = value_str.replace('_', '-')
        try:
            value_list: List[str] = value_str.split("-")
            value_list[-1] = value_list[-1].upper()  # cases like e.g. en-gb
            if len(value_list) == 3:
                value_list[1][0].upper() + value_list[1][1:]  # cases like e.g., yue_Hant_HK = "yue-Hant-HK"
            value_str = '-'.join(value_list)
            instance: Enum = cls(value_str)
            return instance
        except Exception:
            raise ValueError(f"Could not instantiate '{cls.__name__}' from value '{value}'.")

    @staticmethod
    def from_list(language_as_list: List[str], sort_values: bool = True) -> List['LanguageCode']:
        if sort_values:
            return [LanguageCode(language) for language in sorted(language_as_list)]
        else:
            return [LanguageCode(language) for language in language_as_list]

    @classmethod
    def intersect_sets(
        cls,
        set1: Set['LanguageCode'],
        set2: Set['LanguageCode'],
    ) -> Set['LanguageCode']:
        extended_set1: Set['LanguageCode'] = cls.extend_set(set1)
        extended_set2: Set['LanguageCode'] = cls.extend_set(set2)
        intersected_set: Set['LanguageCode'] = extended_set1.intersection(extended_set2)
        return cls.compress_set(intersected_set)

    @classmethod
    def extend_set(cls, lang_set: Set['LanguageCode']) -> Set['LanguageCode']:
        if cls.multi in lang_set:
            return cls.get_all_languages_set()
        return lang_set

    @classmethod
    def compress_set(cls, lang_set: Set['LanguageCode']) -> Set['LanguageCode']:
        if lang_set == cls.get_all_languages_set():
            return {cls.multi}
        return lang_set

    @classmethod
    def get_all_languages_set(cls) -> Set['LanguageCode']:
        all_languages_set: Set['LanguageCode'] = set([lang for lang in cls])
        all_languages_set.remove(cls.multi)
        return all_languages_set

    @staticmethod
    def assert_is_a_language(
        lang: Any,
        raise_exception: bool = True,
    ) -> bool:
        """
        Check if input is a language; log and raise Exception if false

        Args:
            lang (Any): object to be checked for whether it's a LanguageCode
            raise_exception (bool): if true (default) NotALanguageError is raised if check fails

        Returns:
            bool: whether lang is a LanguageCode
        """
        if not lang:
            err_msg = f'{lang} expected to be of type LanguageCode. Obtained type {type(lang)}'
            log.error(err_msg)
            if raise_exception:
                raise NotALanguageError(err_msg)

        is_component_language: bool = isinstance(lang, LanguageCode)
        if not is_component_language:
            err_msg = f'{lang} expected to be of type LanguageCode. Obtained type {type(lang)}'
            log.error(err_msg)
            if raise_exception:
                raise NotALanguageError(err_msg)

        return is_component_language

    def get_language_str(self) -> str:
        """Get the full (lower case) name of the language, e.g. 'english' for LanguageCode.en_US."""
        try:
            language: Optional[Language] = Language.get(self.value)
            assert language
            assert language.language
            language_str: str = language.language
            assert language_str is not None
            return language_str.lower()
        except Exception as e:
            log.error(e)
            raise e

    def get_language(self) -> Language:
        """Get the full (lower case) name of the language, e.g. 'english' for LanguageCode.en_US."""
        try:

            language: Optional[Language] = Language.get(self.value)
            assert language
            return language
        except Exception as e:
            log.error(e)
            raise e

    def get_long_name(self) -> str:
        """Get the full (lower case) name of the language, e.g. 'english' for LanguageCode.en_US.

        Note: this is also the name used by NLTK to identify a language.
        """
        try:
            language: Optional[Language] = Language.get(self.value)
            assert language
            language_name: str = language.language_name().lower()
            return language_name
        except Exception as e:
            log.error(e)
            raise e

    def get_locale(self) -> str:
        if self == LanguageCode.multi:
            return LanguageCode.en_US.get_value()
        else:
            return self.get_value()

    @staticmethod
    @lru_cache(maxsize=3000)
    def get_locales(language_code_str: str) -> Set['LanguageCode']:
        language_locales: Set[str] = LANGUAGE_TO_LOCALES_DICT.get(language_code_str, {'en_US'})
        language_codes: Set['LanguageCode'] = {LanguageCode(language_locale) for language_locale in language_locales}
        return language_codes

    def get_locale_utf(self) -> str:
        # Note: needs to be aligned with linux 'locales' support installed in dockerfiles/ondewo-cai.Dockerfile
        # Locales linux language support: 'dpkg-reconfigure locales' to see available languages
        # Fetch the locale corresponding to the current language code
        return LOCALES_DICT.get(self.name, 'en_US.utf8')  # Default to 'en_US.utf8' if not found

    def get_value(self) -> str:
        return self.value  # type: ignore


# Create the LANGUAGE_TO_LOCALES_DICT
DEFAULT_LANGUAGES: List['LanguageCode'] = [
    LanguageCode.de_DE,
    LanguageCode.en_US,
]

# NOTE(arath): for generation purposes of LANGUAGE_TO_LOCALES_DICT uncomment and execute
# LANGUAGE_TO_LOCALES_DICT: Dict[str, Set[str]] = {}
# for language_code in LanguageCode._member_names_:
#     if isinstance(language_code, str) and language_code != "ValueType":
#         if language_code == "multi":
#             LANGUAGE_TO_LOCALES_DICT["multi"] = {"multi"}
#         else:
#             print(language_code)
#             language_name = Language.get(language_code).language
#             if language_name not in LANGUAGE_TO_LOCALES_DICT:
#                 LANGUAGE_TO_LOCALES_DICT[language_name] = set()
#             LANGUAGE_TO_LOCALES_DICT[language_name].add(language_code)
# print(LANGUAGE_TO_LOCALES_DICT)
