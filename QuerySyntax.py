from typing import Union
import re

class SyntaxError(Exception):
    pass

class Syntax:
    '''Définition et vérification d'une syntaxe
    Une syntaxe est définie par:
    - l'enchaînement des mots clés
    - la quantification de chaque mot-clé
    Une fois que tous les mots-clés ont été ajoutés (.add_keyword) à la "phrase" composée de l'ensemble des mots-clés,
    on vérifie qu'elle est valide (.check).'''
    _regex_prefix_ = r'^'
    _regex_suffix_ = r'$'
    _explain_prefix_ = ''
    _explain_suffix_ = ''

    def __init__(self, *keywords: Union[str, 'Syntax']) -> None:
        self.__keywords = keywords
        self.__sentence = [ ]
    
    def __str__(self) -> str:
        return self._expand()
    
    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {", ".join(map(repr, self.__keywords))}>'
    
    def _expand(self, mode: str=None, prefix='') -> str:
        '''Retourne une chaîne en fonction du mode de génération mode:
        - regex : retourne la regex de la syntaxe
        - explain : retourne une chaîne décrivant la syntaxe, human friendly
        - autre : retourne une chaîne composée des mots-clés de la syntaxe'''
        elements = [ ]
        for keyword in self.__keywords:
            if isinstance(keyword, Syntax):
                elements.append(keyword._expand(mode=mode, prefix=prefix))
            else:
                elements.append(prefix + keyword)
            prefix = ' '
        match mode:
            case 'regex':
                expand_prefix = self._regex_prefix_
                expand_suffix = self._regex_suffix_
            case 'explain':
                expand_prefix = self._explain_prefix_
                expand_suffix = self._explain_suffix_
            case _:
                expand_prefix = ''
                expand_suffix = ''
        expanded = expand_prefix + ''.join(elements) + expand_suffix
        return expanded.upper()
    
    @property
    def regex(self) -> str:
        return self._expand(mode='regex')
    
    @property
    def explain(self) -> str:
        return self._expand(mode='explain')
    
    @property
    def allowed_keywords(self) -> list:
        return self._expand().split(' ')
    
    @property
    def sentence(self) -> str:
        return ' '.join(self.__sentence)
    
    @property
    def definition(self):
        return repr(self)
    
    def add_keyword(self, keyword: str) -> None:
        '''Ajoute un mot-clé à la liste des mots-clés utilisés à vérifier avant exécution de la reqûete'''
        keyword = keyword.upper()
        if self.__keywords and keyword in self.allowed_keywords:
            self.__sentence.append(keyword.upper())
        else:
            raise SyntaxError(f'Unkonwn keyword {keyword}')
    
    def check(self) -> bool:
        '''Vérifie que la phrase composée des mots-clés correspond à l'expression régulière de la syntaxe'''
        if not self.__keywords:
            return True
        if re.match(self.regex, self.sentence):
            return True
        raise SyntaxError(f'Keyword sequence `{self.sentence}` does not match syntax `{self.explain}`')

class Once(Syntax):
    '''Mot-lé présent exactement UNE fois'''
    _regex_prefix_ = r'('
    _regex_suffix_ = r')'
    _explain_prefix_ = ''
    _explain_suffix_ = ''

class NoneOrOnce(Syntax):
    '''Mot-lé présent ZERO ou UNE fois'''
    _regex_prefix_ = r'('
    _regex_suffix_ = r')?'
    _explain_prefix_ = '['
    _explain_suffix_ = ']'
    
class NoneOrMore(Syntax):
    '''Mot-lé présent ou pas, en un nombre indéfini d'exemplaires'''
    _regex_prefix_ = r'('
    _regex_suffix_ = r')*'
    _explain_prefix_ = '['
    _explain_suffix_ = ']...'

class OnceOrMore(Syntax):
    '''Mot-lé présent une fois ou plus'''
    _regex_prefix_ = r'('
    _regex_suffix_ = r')+'
    _explain_prefix_ = ''
    _explain_suffix_ = '(...)'

class SelectQuerySyntax(Syntax):
     def __init__(self):
         super().__init__(
            Once('select'),
            Once('from'),
            NoneOrMore('join', NoneOrOnce('on')),
            NoneOrOnce('where'),
            NoneOrOnce('order_by'),
            NoneOrOnce('limit'),
         )

class UpdateQuerySyntax(Syntax):
    def __init__(self):
        super().__init__(
            Once('update'),
            Once('set'),
            NoneOrOnce('where')
        )

class DeleteQuerySyntax(Syntax):
    def __init__(self):
        super().__init__(
            Once('delete'),
            Once('from'),
            NoneOrOnce('where')
        )

class DropQuerySyntax(Syntax):
    def __init__(self):
        super().__init__(
            Once('alter'),
            Once('drop'),
            NoneOrOnce('where')
        )
