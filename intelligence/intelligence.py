from controller.matches_controllers import MatchesController
from controller.statistics_controller import StatisticsController
from models.statistics import Statistics
from utils.constants import WINNER, LOSER, DRAW
from utils.utils import Utils
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression


class Intelligence():
    def __init__(self, team_home_id, team_way_id):
        # Id do time da casa
        self.team_home_id = team_home_id

        # Id do time visitante
        self.team_way_id = team_way_id

        #Lista de estatísticas
        self.data = []

        # Lista dos Resultados para cada Estatístisca
        self.target = []

        #Dividir os dados em conjuntos de treino e teste
        self.X_train = []
        self.X_test = []
        self.y_train = []
        self.y_test = []

        self.modelo = None


    def start(self):
        result = self.pass1()
        if result != None:
            return result

        result = self.pass2()
        if result != None:
            return result

        result = self.pass3()
        return result


    # Pesquisando partidas entre Palmeiras e Flamengo onde o Palmeiras era o mandante
    def pass1(self):
        macthes = MatchesController()
        list = macthes.get_by_all_per_team(self.team_home_id, self.team_way_id)

        if len(list) == 0:
            return "Não há dados de partidas entre estes dois times"

        for matche in list:
            statistics_team_home = StatisticsController().get_by_statistics_per_matche_id(matche.id, matche.team_home_id)
            statistics_team_away = StatisticsController().get_by_statistics_per_matche_id(matche.id, matche.team_away_id)

            result = 0
            if matche.draw:
                result = DRAW
            elif matche.winner_home:
                result = WINNER
            else:
                result = LOSER

            self.generate_data(statistics_team_home, statistics_team_away, result)

        self.fix_bug_is_only_one_game()

    # A máquina está sendo treinada
    def pass2(self):
        return self.training_machine()


    # Prevendo o próximo jogo
    def pass3(self):
        result_of_game_probability = self.predict_next_game_based_on_last_five_games()
        return result_of_game_probability


    #Adiciona os dados no atributo data, que servirá de base para o aprendizado de máquina
    def generate_data(self, statistic, statistic2, result):
        if isinstance(statistic, Statistics) and isinstance(statistic2, Statistics):
            self.target.append(result)
            utils = Utils()
            self.data.append(utils.mounted_data_machine_learning(statistic, statistic2))
        else:
            raise TypeError("O argumento deve do tipo Statistics.")

    #Bug que acontece ao treinar a máquina quando só tem um jogo disponivel na base
    def fix_bug_is_only_one_game(self):
        if len(self.data) == 1:
            self.data.append(self.data[0])
            self.target.append(self.target[0])



    def training_machine(self):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                self.data,
                self.target,
                test_size=0.2,
                random_state=42
            )

        if  len(self.y_train) == 1:
            return self.y_train

        if Utils().verify_unic_array(self.y_train):
            return self.y_train
            # do something else

        # Inicializar e treinar o modelo de regressão logística
        self.modelo = LogisticRegression(multi_class='multinomial', solver='lbfgs', max_iter=1000)
        self.modelo.fit(self.X_train, self.y_train)

    # Tenta prever o próximo jogo gerando a média das estásticas dos ultimos 5 jogos como previsão
    def predict_next_game_based_on_last_five_games(self):
        # Fazendo a média de cada estatísticas com os últimos 5 jogos
        linhas_selecionadas = self.data[(len(self.data) - 5):len(self.data)]

        # Calculando a média de cada coluna
        media_colunas = [sum(coluna) / len(coluna) for coluna in zip(*linhas_selecionadas)]

        previsoes =  self.modelo.predict([media_colunas])
        return previsoes










