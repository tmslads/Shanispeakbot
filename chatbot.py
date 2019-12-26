# The Shani Sir chatbot

import chatterbot
##from chatterbot.trainers import ChatterBotCorpusTrainer

shanisirbot = chatterbot.ChatBot('The Shani Sir Bot',
                                 storage_adapter='chatterbot.storage.SQLStorageAdapter',
                                 logic_adapters=['chatterbot.logic.BestMatch',                                                 
                                                 'chatterbot.logic.SpecificResponseAdapter',
                                                 'chatterbot.logic.TimeLogicAdapter',
                                                 'chatterbot.logic.MathematicalEvaluation',
                                                 'chatterbot.logic.UnitConversion',],
                                 preprocessors=['chatterbot.preprocessors.clean_whitespace'],
                                 read_only=True)

##corpora_trainer = ChatterBotCorpusTrainer(shanisirbot)
##corpora_trainer.train("chatterbot.corpus.english")
