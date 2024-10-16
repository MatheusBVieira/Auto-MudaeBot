class Texts:
    ENGLISH = {
        'next_claim_reset': "The next claim reset is in",
        'cant_claim_for_another': "you can't claim for another",
        'next_rolls_reset': "Next rolls reset in",
        'you_have_rolls_left': "You have",
        'rolls_left': "rolls left"
    }

    PORTUGUESE = {
        'next_claim_reset': "O próximo reset de claim será em",
        'cant_claim_for_another': "você não pode fazer claim por mais",
        'next_rolls_reset': "O próximo reset de rolls será em",
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
