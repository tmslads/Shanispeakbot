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
                                 read_only=False)  # This disables further learning from conversations the bot has

def train_with(corpus):
    """
    Trains the bot using the specified corpus
    eng ---> chatterbot.corpus.english (standard English corpus from chatterbot_corpora)
    woz ---> ./MULTIWOZ2.1 (Multi-Domain Wizard-of-Oz dataset from http://dialogue.mi.eng.cam.ac.uk/index.php/corpus/)
    ubu ---> Will download and extract the Ubuntu dialog corpus if that has not already been done.
    """

    from chatterbot.trainers import ChatterBotCorpusTrainer, UbuntuCorpusTrainer
    import time

    if corpus == 'ubu':
        start = time.time()
        corpus_trainer = UbuntuCorpusTrainer(shanisirbot)
        corpus_trainer.train()
    else:
        start = time.time()
        corpus_trainer = ChatterBotCorpusTrainer(shanisirbot)
        if corpus == 'eng':
            corpus_trainer.train("chatterbot.corpus.english")
        elif corpus == 'woz':
            corpus_trainer.train("./MULTIWOZ2.1")
        else:
            print("Invalid corpus.")
            return
    end = time.time()
    time_taken = end - start
    print(f"\n\nThe Shani Sir chatbot has been trained using the corpus {corpus}. Time taken: {time_taken}s")

