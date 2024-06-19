
import re
from typing import cast


class TSInformation:
    """ 番組情報のユーティリティ (KonomiTV から移植) """

    # formatString() で使用する変換マップ
    __format_string_translation_map: dict[int, str] | None = None
    __format_string_regex: re.Pattern[str] | None = None
    __format_string_regex_table: dict[str, str] | None = None


    @classmethod
    def __buildFormatStringTranslationMap(cls) -> None:
        """
        formatString() で使用する変換マップや正規表現を構築する
        一度のみ実行され、以降はキャッシュされる
        """

        # すでに構築済みの場合は何もしない
        if cls.__format_string_translation_map is not None and cls.__format_string_regex is not None:
            return

        # 全角英数を半角英数に置換
        # ref: https://github.com/ikegami-yukino/jaconv/blob/master/jaconv/conv_table.py
        zenkaku_table = '０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ'
        hankaku_table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'
        merged_table = dict(zip(list(zenkaku_table), list(hankaku_table)))

        # 全角記号を半角記号に置換
        symbol_zenkaku_table = '＂＃＄％＆＇（）＋，－．／：；＜＝＞［＼］＾＿｀｛｜｝　'
        symbol_hankaku_table = '"#$%&\'()+,-./:;<=>[\\]^_`{|} '
        merged_table.update(zip(list(symbol_zenkaku_table), list(symbol_hankaku_table)))
        merged_table.update({
            # 一部の半角記号を全角に置換
            # 主に見栄え的な問題（全角の方が字面が良い）
            '!': '！',
            '?': '？',
            '*': '＊',
            '~': '～',
            # シャープ → ハッシュ
            '♯': '#',
            # 波ダッシュ → 全角チルダ
            ## EDCB は ～ を全角チルダとして扱っているため、KonomiTV でもそのように統一する
            ## TODO: 番組検索を実装する際は検索文字列の波ダッシュを全角チルダに置換する下処理が必要
            ## ref: https://qiita.com/kasei-san/items/3ce2249f0a1c1af1cbd2
            '〜': '～',
        })

        # 番組表で使用される囲み文字の置換テーブル
        ## ref: https://note.nkmk.me/python-chr-ord-unicode-code-point/
        ## ref: https://github.com/l3tnun/EPGStation/blob/v2.6.17/src/util/StrUtil.ts#L7-L46
        ## ref: https://github.com/xtne6f/EDCB/blob/work-plus-s-230526/EpgDataCap3/EpgDataCap3/ARIB8CharDecode.cpp#L1324-L1614
        enclosed_characters_table = {
            '\U0001f14a': '[HV]',
            '\U0001f14c': '[SD]',
            '\U0001f13f': '[P]',
            '\U0001f146': '[W]',
            '\U0001f14b': '[MV]',
            '\U0001f210': '[手]',
            '\U0001f211': '[字]',
            '\U0001f212': '[双]',
            '\U0001f213': '[デ]',
            '\U0001f142': '[S]',
            '\U0001f214': '[二]',
            '\U0001f215': '[多]',
            '\U0001f216': '[解]',
            '\U0001f14d': '[SS]',
            '\U0001f131': '[B]',
            '\U0001f13d': '[N]',
            '\U0001f217': '[天]',
            '\U0001f218': '[交]',
            '\U0001f219': '[映]',
            '\U0001f21a': '[無]',
            '\U0001f21b': '[料]',
            '\U0001f21c': '[前]',
            '\U0001f21d': '[後]',
            '\U0001f21e': '[再]',
            '\U0001f21f': '[新]',
            '\U0001f220': '[初]',
            '\U0001f221': '[終]',
            '\U0001f222': '[生]',
            '\U0001f223': '[販]',
            '\U0001f224': '[声]',
            '\U0001f225': '[吹]',
            '\U0001f14e': '[PPV]',
            '\U0001f200': '[ほか]',
        }

        # Unicode の囲み文字を大かっこで囲った文字に置換する
        ## EDCB で EpgDataCap3_Unicode.dll を利用している場合や、Mirakurun 3.9.0-beta.24 以降など、
        ## 番組情報取得元から Unicode の囲み文字が送られてくる場合に対応するためのもの
        ## Unicode の囲み文字はサロゲートペアなどで扱いが難しい上に KonomiTV では囲み文字を CSS でハイライトしているため、Unicode にするメリットがない
        ## ref: https://note.nkmk.me/python-str-replace-translate-re-sub/
        merged_table.update(enclosed_characters_table)

        # 変換マップを構築し、クラス変数に格納
        cls.__format_string_translation_map = str.maketrans(merged_table)

        # 逆に代替の文字表現に置換された ARIB 外字を Unicode に置換するテーブル
        ## 主に EDCB (EpgDataCap3_Unicode.dll 不使用) 環境向けの処理
        ## EDCB は通常 Shift-JIS で表現できない文字をサロゲートペア範囲外の文字も含めてすべて代替の文字表現に変換するが、これはこれで見栄えが悪い
        ## そこで、サロゲートペアなしで表現できて、一般的な日本語フォントでグリフが用意されていて、
        ## かつ他の文字表現から明確に判別可能でそのままでは分かりづらい文字表現だけ Unicode に置換する
        ## ref: https://github.com/xtne6f/EDCB/blob/work-plus-s-230526/EpgDataCap3/EpgDataCap3/ARIB8CharDecode.cpp#L1324-L1614
        cls.__format_string_regex_table = {
            # '[・]': '⚿',  # グリフが用意されていないことが多い
            '(秘)': '㊙',
            'm^2': 'm²',
            'm^3': 'm³',
            'cm^2': 'cm²',
            'cm^3': 'cm³',
            'km^2': 'km²',
            '[社]': '㈳',
            '[財]': '㈶',
            '[有]': '㈲',
            '[株]': '㈱',
            '[代]': '㈹',
            # '(問)': '㉄',  # グリフが用意されていないことが多い
            '^2': '²',
            '^3': '³',
            # '(箏): '㉇',  # グリフが用意されていないことが多い
            '(〒)': '〶',
            '()()': '⚾',
        }

        # 正規表現を構築し、クラス変数に格納
        cls.__format_string_regex = re.compile("|".join(map(re.escape, cls.__format_string_regex_table.keys())))


    @classmethod
    def formatString(cls, string: str) -> str:
        """
        文字列に含まれる英数や記号を半角に置換し、一律な表現に整える

        Args:
            string (str): 文字列

        Returns:
            str: 置換した文字列
        """

        result = string

        # 変換マップを構築 (初回以降はキャッシュされる)
        cls.__buildFormatStringTranslationMap()
        assert cls.__format_string_translation_map is not None
        assert cls.__format_string_regex is not None
        assert cls.__format_string_regex_table is not None

        # 置換を実行
        result = result.translate(cls.__format_string_translation_map)
        result = cls.__format_string_regex.sub(lambda match: cast(dict[str, str], cls.__format_string_regex_table)[match.group(0)], result)

        # 置換した文字列を返す
        return result
