import pygame
import random # Importa o módulo random para gerar números aleatórios

# 1. Inicialização do Pygame
pygame.init()

# 2. Configurações da Tela
LARGURA_TELA = 800
ALTURA_TELA = 600
tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
pygame.display.set_caption("Ovelha Corredora") # Título da janela

# --- CONTROLE DE TEMPO E FPS ---
clock = pygame.time.Clock()
FPS = 60

# 3. Cores (em formato RGB - Vermelho, Verde, Azul)
AZUL_CLARO = (173, 216, 230) # Um azul mais claro para o céu


# ====================================================================
# CONFIGURAÇÃO DE FONTES PARA TEXTO (Pontuação, Nível, Game Over)
# ====================================================================
font = pygame.font.Font(None, 36)       # Fonte para pontuação e nível
game_over_font = pygame.font.Font(None, 72) # Fonte maior para "FIM DE JOGO!"
# ====================================================================

# Flag para desenhar caixas de colisão para debug (True/False)
DEBUG_DRAW_COLLISION = False


# --- CARREGANDO AS IMAGENS ---
try:
    ovelha_parada_img = pygame.image.load('assets/ovelha_parada.png').convert_alpha()
    ovelha_andando_1_img = pygame.image.load('assets/ovelha_andando_1.png').convert_alpha()
    ovelha_andando_2_img = pygame.image.load('assets/ovelha_andando_2.png').convert_alpha()
    ovelha_pulando_img = pygame.image.load('assets/ovelha_pulando.png').convert_alpha()
    arbusto_img = pygame.image.load('assets/arbusto.png').convert_alpha()
    # Plano de fundo (dia)
    plano_fundo_img = pygame.image.load('assets/plano_fundo_dia.png').convert()
    # Escala o plano de fundo para preencher toda a janela (evita partes em preto ou duplicadas)
    plano_fundo_img = pygame.transform.scale(plano_fundo_img, (LARGURA_TELA, ALTURA_TELA))
    # Tenta carregar o plano de fundo noturno (fallback se não existir)
    try:
        plano_fundo_noite_img = pygame.image.load('assets/plano_fundo_noite.png').convert()
        plano_fundo_noite_img = pygame.transform.scale(plano_fundo_noite_img, (LARGURA_TELA, ALTURA_TELA))
    except pygame.error:
        plano_fundo_noite_img = None
    # Tenta carregar uma imagem de moeda; se não existir, cria uma superfície simples
    try:
        moeda_img = pygame.image.load('assets/moeda.png').convert_alpha()
    except pygame.error:
        moeda_img = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(moeda_img, (255, 223, 0), (10, 10), 9)
except pygame.error as e:
    print(f"Erro ao carregar imagem: {e}")
    print("Verifique se a pasta 'assets' existe e se os nomes dos arquivos estão corretos.")
    print("Ex: 'assets/ovelha_parada.png'")
    pygame.quit()
    exit()

# --- ANIMAÇÃO DA OVELHA ---
animacao_ovelha_andando = [ovelha_andando_1_img, ovelha_andando_2_img]
frame_atual_ovelha = 0
velocidade_animacao_ovelha = 8
contador_animacao_ovelha = 0

# --- POSIÇÃO INICIAL DA OVELHA ---
pos_x_ovelha = 50
pos_y_ovelha = ALTURA_TELA - ovelha_parada_img.get_height() - 10

# --- ESTADO DO PULO DA OVELHA ---
pulando = False
velocidade_pulo = 0
gravidade = 0.8         # Gravidade ligeiramente menor
forca_pulo_inicial = -20 # Força de pulo inicial maior (negativo para subir)
pos_y_ovelha_chao = pos_y_ovelha # Guarda a posição Y original do chão

# ====================================================================
# AJUSTES PARA CAIXAS DE COLISÃO (RECTANGLES) - NOVOS VALORES!
# Estes valores foram ajustados para tornar a colisão mais precisa.
# Você pode alterá-los para "diminuir" ou "aumentar" a caixa de colisão
# em relação à imagem visual.
# ====================================================================
# Ovelha: Reduz a altura e desloca para focar na base do corpo
OVELHA_COLLISION_WIDTH_REDUCTION = 10 # Reduz 10px da largura total da ovelha
OVELHA_COLLISION_HEIGHT_REDUCTION = 20 # Reduz 20px da altura total da ovelha
OVELHA_COLLISION_OFFSET_X = 5 # Desloca a caixa 5px para a direita
OVELHA_COLLISION_OFFSET_Y = 20 # Desloca a caixa 20px para baixo (para focar nos pés)

# Arbusto: Reduz a largura e altura da caixa de colisão, focando na parte "sólida"
ARBUSTO_COLLISION_WIDTH_REDUCTION = 20 # Reduz 20px da largura total (10px de cada lado)
ARBUSTO_COLLISION_HEIGHT_REDUCTION = 15 # Reduz 15px da altura total
ARBUSTO_COLLISION_OFFSET_X = 10 # Desloca a caixa 10px para a direita
ARBUSTO_COLLISION_OFFSET_Y = 5 # Desloca a caixa 5px para baixo
# Ajuste visual: eleva o arbusto alguns pixels para ficar acima do chão e forçar o pulo
ARBUSTO_VISUAL_RAISE = 20  # Eleva o arbusto em px (aumente para torná-lo mais alto)
# ====================================================================

# Fator que determina a fração da altura do pulo onde a moeda aparecerá.
# 1.0 = exatamente no pico; valores <1.0 deixam a moeda mais baixa (perto do chão).
COIN_JUMP_HEIGHT_FACTOR = 0.7

# ====================================================================
# VARIÁVEIS DO JOGO: PONTUAÇÃO, NÍVEL E ESTADO DO JOGO
# ====================================================================
score = 0
level = 1
score_for_next_level = 10 # Pontos necessários para avançar para o próximo nível (Ajustado para teste)
LEVEL_UP_SCORE_INCREMENT = 10 # Quantos pontos a mais para o próximo nível após cada nível (Ajustado para teste)

game_over = False # Flag para controlar o estado de fim de jogo

# ====================================================================
# VARIÁVEIS E LISTA PARA MÚLTIPLOS ARBUSTOS E VELOCIDADE VARIÁVEL
# ====================================================================
# Parâmetros base para a velocidade do jogo (irão aumentar com o nível)
BASE_MIN_GAME_SPEED = 4  # Ajustado: Velocidade mínima base um pouco mais rápida
BASE_MAX_GAME_SPEED = 8  # Ajustado: Velocidade máxima base um pouco mais rápida
SPEED_INCREMENT_PER_LEVEL = 0.5 # Aumento de velocidade por nível

# (velocidade_jogo será definida como fixa mais abaixo)

arbustos = [] # Lista para armazenar todos os arbustos ativos na tela. Cada arbusto será um dicionário: {'x': pos_x, 'y': pos_y}

# Variáveis para controlar a geração de novos arbustos
last_bush_spawn_time = pygame.time.get_ticks() # Tempo em ms do último arbusto gerado
min_time_between_bushes = 1000  # Mínimo de 1.0 segundos para o próximo arbusto
max_time_between_bushes = 2000 # Máximo de 2.0 segundos para o próximo arbusto
next_bush_spawn_interval = random.randint(min_time_between_bushes, max_time_between_bushes)

# Lista de moedas colecionáveis (uma por arbusto)
moedas = []

# Velocidade fixa do jogo (removido sistema de velocidade alternada). Usamos média do range base.
velocidade_jogo = int((BASE_MIN_GAME_SPEED + BASE_MAX_GAME_SPEED) / 2)

# Estado do fundo: False = dia, True = noite
is_night = False


# Função auxiliar para obter a posição Y do arbusto (sempre no chão)
def get_bush_y_pos():
    return ALTURA_TELA - arbusto_img.get_height() - 10


# Calcula o deslocamento vertical máximo do pulo (em px) baseado na física simples:
# Usamos iteração para simular o movimento até a velocidade_pulo se tornar >= 0 (pico)
def calcular_altura_pulo_max():
    v = forca_pulo_inicial
    y = 0
    # iterar até começar a cair (velocidade positiva)
    while v < 0:
        y += v
        v += gravidade
    # y será negativo (subida), retornamos deslocamento em px (negativo)
    return int(y)

# ====================================================================
# FUNÇÃO PARA RESETAR O JOGO
# ====================================================================
def reset_game():
    global score, level, score_for_next_level, game_over, arbustos, last_bush_spawn_time, next_bush_spawn_interval, velocidade_jogo, pulando, velocidade_pulo, pos_y_ovelha, frame_atual_ovelha, contador_animacao_ovelha
    score = 0
    level = 1
    score_for_next_level = 10 # Reinicia para o valor de teste
    game_over = False
    arbustos = []
    last_bush_spawn_time = pygame.time.get_ticks()
    # Recalcula o intervalo inicial para o próximo arbusto
    next_bush_spawn_interval = random.randint(min_time_between_bushes, max_time_between_bushes)
    # Recalcula a velocidade inicial do jogo para o Nível 1
    # Mantém velocidade fixa ao reiniciar (média do range base mais incremento por nível)
    velocidade_jogo = int((BASE_MIN_GAME_SPEED + BASE_MAX_GAME_SPEED) / 2 + (level - 1) * SPEED_INCREMENT_PER_LEVEL)
    # Limpa moedas
    global moedas
    moedas = []
    # Reset do fundo para dia
    global is_night
    is_night = False
    pulando = False
    velocidade_pulo = 0
    pos_y_ovelha = pos_y_ovelha_chao # Garante que a ovelha volte para o chão
    frame_atual_ovelha = 0
    contador_animacao_ovelha = 0
# ====================================================================


# 4. Loop Principal do Jogo
rodando = True
while rodando:
    # 5. Tratamento de Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        elif evento.type == pygame.KEYDOWN:
            if game_over: # Se o jogo acabou, permite reiniciar
                if evento.key == pygame.K_r: # Pressione 'R' para reiniciar
                    reset_game()
            else: # Se o jogo estiver rodando, processa o pulo
                if evento.key == pygame.K_SPACE and not pulando:
                    pulando = True
                    velocidade_pulo = forca_pulo_inicial
                    # A pontuação NÃO aumenta mais ao pular. Agora só ao coletar moedas.


    # ====================================================================
    # LÓGICA DE JOGO SÓ RODA SE NÃO FOR GAME OVER
    # ====================================================================
    if not game_over:
        # 6. Desenha o plano de fundo (imagem) ou fallback para cor
        try:
            # Desenha dia ou noite dependendo do estado
            if is_night and 'plano_fundo_noite_img' in globals() and plano_fundo_noite_img is not None:
                tela.blit(plano_fundo_noite_img, (0, 0))
            else:
                tela.blit(plano_fundo_img, (0, 0))
        except NameError:
            tela.fill(AZUL_CLARO)

        # --- LÓGICA DE PULO DA OVELHA ---
        if pulando:
            pos_y_ovelha += velocidade_pulo
            velocidade_pulo += gravidade

            if pos_y_ovelha >= pos_y_ovelha_chao:
                pos_y_ovelha = pos_y_ovelha_chao
                pulando = False
                velocidade_pulo = 0

        # --- ATUALIZAÇÃO E DESENHO DA IMAGEM DA OVELHA ---
        imagem_ovelha_atual = None

        if pulando:
            imagem_ovelha_atual = ovelha_pulando_img
        else:
            contador_animacao_ovelha += 1
            if contador_animacao_ovelha >= velocidade_animacao_ovelha:
                contador_animacao_ovelha = 0
                frame_atual_ovelha = (frame_atual_ovelha + 1) % len(animacao_ovelha_andando)
            imagem_ovelha_atual = animacao_ovelha_andando[frame_atual_ovelha]

        # Desenha a imagem da ovelha na tela
        if imagem_ovelha_atual:
            tela.blit(imagem_ovelha_atual, (pos_x_ovelha, pos_y_ovelha)) # Desenha a imagem na pos original

        # Cria o retângulo da ovelha para detecção de colisão, com ajustes
        # Usar as dimensões da imagem atualmente desenhada (pulando ou frame andando)
        current_ovelha_img = imagem_ovelha_atual if imagem_ovelha_atual is not None else ovelha_parada_img
        ovelha_rect = pygame.Rect(pos_x_ovelha + OVELHA_COLLISION_OFFSET_X,
                                  pos_y_ovelha + OVELHA_COLLISION_OFFSET_Y,
                                  current_ovelha_img.get_width() - OVELHA_COLLISION_WIDTH_REDUCTION,
                                  current_ovelha_img.get_height() - OVELHA_COLLISION_HEIGHT_REDUCTION)

        # Desenhar retângulos de colisão para debug, se habilitado
        if DEBUG_DRAW_COLLISION:
            pygame.draw.rect(tela, (255, 0, 0), ovelha_rect, 2)


        # --- LÓGICA DE VELOCIDADE (FIXA) ---
        current_time = pygame.time.get_ticks() # Pega o tempo atual do jogo em milissegundos


        # --- LÓGICA DE GERAÇÃO, MOVIMENTO E DESENHO DE MÚLTIPLOS ARBUSTOS ---
        if current_time - last_bush_spawn_time > next_bush_spawn_interval:
            # Adiciona um novo arbusto à lista
            bush_x = LARGURA_TELA
            bush_y = get_bush_y_pos()
            arbustos.append({'x': bush_x, 'y': bush_y})
            # Cria uma moeda centralizada sobre o arbusto na altura máxima do pulo
            moeda_x = bush_x + (arbusto_img.get_width() - moeda_img.get_width()) // 2
            altura_pulo = calcular_altura_pulo_max()  # valor negativo (subida)
            # reduzimos a altura do pico com um fator para posicionar a moeda mais baixa
            altura_pulo_ajustada = int(altura_pulo * COIN_JUMP_HEIGHT_FACTOR)
            # posição y da moeda: chão + deslocamento ajustado do pico - altura da moeda
            moeda_y = pos_y_ovelha_chao + altura_pulo_ajustada - moeda_img.get_height()
            # garante que não fique acima do topo da tela
            if moeda_y < 0:
                moeda_y = 5
            moedas.append({'x': moeda_x, 'y': moeda_y, 'collected': False})
            last_bush_spawn_time = current_time
            next_bush_spawn_interval = random.randint(min_time_between_bushes, max_time_between_bushes)

        bushes_to_remove = []
        for bush in arbustos:
            bush['x'] -= velocidade_jogo # O arbusto se move com a velocidade_jogo atual
            # Cria o retângulo do arbusto para detecção de colisão, com ajustes
            bush_rect = pygame.Rect(bush['x'] + ARBUSTO_COLLISION_OFFSET_X,
                                    bush['y'] + ARBUSTO_COLLISION_OFFSET_Y,
                                    arbusto_img.get_width() - ARBUSTO_COLLISION_WIDTH_REDUCTION,
                                    arbusto_img.get_height() - ARBUSTO_COLLISION_HEIGHT_REDUCTION)
            tela.blit(arbusto_img, (bush['x'], bush['y'])) # Desenha a imagem na pos original
            # Desenhar retângulo de colisão do arbusto para debug, se habilitado
            if DEBUG_DRAW_COLLISION:
                pygame.draw.rect(tela, (0, 255, 0), bush_rect, 2)
            # --------------------------------------------------------------------------------

            # ====================================================================
            # LÓGICA DE COLISÃO
            # ====================================================================
            # Verifica colisão entre a ovelha e o arbusto
            if ovelha_rect.colliderect(bush_rect):
                game_over = True # Define game_over como True se houver colisão
            # ====================================================================

            if bush['x'] < -arbusto_img.get_width():
                bushes_to_remove.append(bush)

        # Atualiza e desenha moedas
        moedas_para_remover = []
        for moeda in moedas:
            if moeda.get('collected'):
                moedas_para_remover.append(moeda)
                continue
            moeda['x'] -= velocidade_jogo
            moeda_rect = pygame.Rect(moeda['x'], moeda['y'], moeda_img.get_width(), moeda_img.get_height())
            tela.blit(moeda_img, (moeda['x'], moeda['y']))
            # Desenhar retângulo de colisão da moeda para debug, se habilitado
            if DEBUG_DRAW_COLLISION:
                pygame.draw.rect(tela, (255, 215, 0), moeda_rect, 1)
            # Verifica colisão com a ovelha
            if ovelha_rect.colliderect(moeda_rect):
                moeda['collected'] = True
                score += 1
                # Alterna o fundo a cada 5 pontos (quando atinge múltiplo de 5)
                if score % 5 == 0:
                    is_night = not is_night
            # Remove se saiu da tela
            if moeda['x'] < -moeda_img.get_width():
                moedas_para_remover.append(moeda)

        for m in moedas_para_remover:
            if m in moedas:
                moedas.remove(m)

        for bush in bushes_to_remove:
            arbustos.remove(bush)

        # ====================================================================
        # LÓGICA DE PONTUAÇÃO E NÍVEL
        # ====================================================================
        # current_time já foi obtido acima

        if score >= score_for_next_level:
            level += 1
            score_for_next_level += LEVEL_UP_SCORE_INCREMENT # Aumenta o próximo limite de pontuação
            print(f"Subiu para o Nível {level}!")
            # Atualiza velocidade fixa com incremento por nível
            velocidade_jogo = int((BASE_MIN_GAME_SPEED + BASE_MAX_GAME_SPEED) / 2 + (level - 1) * SPEED_INCREMENT_PER_LEVEL)
        # ====================================================================

    # ====================================================================
    # EXIBIÇÃO DA PONTUAÇÃO, NÍVEL E TELA DE GAME OVER
    # ====================================================================
    score_text = font.render(f"Pontuação: {score}", True, (0, 0, 0)) # Texto preto
    level_text = font.render(f"Nível: {level}", True, (0, 0, 0))    # Texto preto

    tela.blit(score_text, (LARGURA_TELA - score_text.get_width() - 20, 20)) # Canto superior direito
    tela.blit(level_text, (LARGURA_TELA - level_text.get_width() - 20, 60)) # Abaixo da pontuação

    if game_over:
        game_over_text = game_over_font.render("FIM DE JOGO!", True, (255, 0, 0)) # Texto "FIM DE JOGO!" em vermelho
        restart_text = font.render("Pressione 'R' para Reiniciar", True, (0, 0, 0)) # Texto de reinício em preto

        # Centraliza o texto "FIM DE JOGO!"
        game_over_rect = game_over_text.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 - 40))
        tela.blit(game_over_text, game_over_rect)

        # Centraliza o texto de reiniciar abaixo
        restart_rect = restart_text.get_rect(center=(LARGURA_TELA // 2, ALTURA_TELA // 2 + 20))
        tela.blit(restart_text, restart_rect)
    # ====================================================================


    # 7. Atualização da Tela
    pygame.display.flip()

    # --- CONTROLA O FPS ---
    clock.tick(FPS)

# 8. Finalização do Pygame
pygame.quit()
