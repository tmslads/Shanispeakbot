# The Shani Sir chatbot
import chatterbot

shanisirbot = chatterbot.ChatBot('The Shani Sir Bot',
                                 storage_adapter='chatterbot.storage.SQLStorageAdapter',
                                 logic_adapters=['chatterbot.logic.BestMatch',                                                 
                                                 'chatterbot.logic.SpecificResponseAdapter',
                                                 'chatterbot.logic.TimeLogicAdapter',
                                                 'chatterbot.logic.MathematicalEvaluation',
                                                 'chatterbot.logic.UnitConversion',],
                                 preprocessors=['chatterbot.preprocessors.clean_whitespace'],
                                 read_only=True)  # This disables further learning from conversations the bot has


def train_him():
    """Trains the bot using the standard English corpora (for now)"""

    from chatterbot.trainers import ChatterBotCorpusTrainer
    import time

    corpora_trainer = ChatterBotCorpusTrainer(shanisirbot)
    start = time.time()
    corpora_trainer.train("chatterbot.corpus.english")
    end = time.time()
    time_taken = end - start
    print("\n\nThe Shani Sir Bot has been trained using the English corpora. Time taken: {time_taken}s")

