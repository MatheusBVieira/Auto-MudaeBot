class Texts:
    ENGLISH = {
        'claim': "claim",
        'next_claim_reset': "The next claim reset is in",
        'cant_claim_for_another': "you can't claim for another",
        'next_rolls_reset': "Next rolls reset in",
        'you_have_rolls_left': "You have",
        'rolls_left': "rolls left"
    }

    PORTUGUESE = {
        'claim': "casar",
        'next_claim_reset': "casar agora mesmo! A próxima reinicialização é em",
        'cant_claim_for_another': "falta um tempo antes que você possa se casar novamente",
        'next_rolls_reset': "A próxima reinicialização é em",
        'you_have_rolls_left': "Você tem",
        'rolls_left': "rolls restantes"
    }

    current_language = ENGLISH 

    @classmethod
    def set_language(cls, language):
        if language.lower() == 'portuguese':
            cls.current_language = cls.PORTUGUESE
        else:
            cls.current_language = cls.ENGLISH
