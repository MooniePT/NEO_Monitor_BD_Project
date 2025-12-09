//////////////////////////////////////////////////////
// Tabelas principais
//////////////////////////////////////////////////////

Table Asteroide {
  id_asteroide           int          [pk, increment]
  id_csv                 int
  id_spk                 int
  nome_completo          varchar(255)
  pdes                   varchar(20)
  nome_asteroide         varchar(100)
  prefixo                varchar(20)
  flag_neo               boolean
  flag_pha               boolean
  H_mag                  decimal(5,2)
  diametro_km            decimal(10,4)
  diametro_sigma_km      decimal(10,4)
  albedo                 decimal(6,4)
  data_descoberta        date
}

Table Classe_Orbital {
  codigo_classe          varchar(20)  [pk]
  descricao              varchar(255)
}

Table Solucao_Orbital {
  id_solucao_orbital     int          [pk, increment]
  id_asteroide           int          [not null]           // FK -> Asteroide
  codigo_classe          varchar(20)  [not null]           // FK -> Classe_Orbital
  id_orbita_externa      varchar(50)

  epoca_jd               decimal(15,5)
  epoca_mjd              decimal(15,5)
  epoca_cal              varchar(25)
  equinocio              varchar(10)

  excentricidade         decimal(12,10)
  semi_eixo_maior_ua     decimal(13,10)
  perielio_ua            decimal(13,10)
  inclinacao_graus       decimal(10,6)
  long_no_asc_graus      decimal(10,6)
  arg_perielio_graus     decimal(10,6)
  anomalia_media_graus   decimal(10,6)
  afelio_ua              decimal(13,10)
  movimento_medio_graus_dia decimal(12,8)
  tempo_perielio_jd      decimal(15,5)
  tempo_perielio_cal     varchar(25)
  periodo_dias           decimal(12,5)
  periodo_anos           decimal(12,5)
  moid_ua                decimal(13,10)
  moid_ld                decimal(13,10)

  sigma_e                decimal(12,10)
  sigma_a_ua             decimal(13,10)
  sigma_q_ua             decimal(13,10)
  sigma_i_graus          decimal(10,6)
  sigma_om_graus         decimal(10,6)
  sigma_w_graus          decimal(10,6)
  sigma_ma_graus         decimal(10,6)
  sigma_ad_ua            decimal(13,10)
  sigma_n_graus_dia      decimal(12,8)
  sigma_tp_jd            decimal(15,5)
  sigma_periodo_dias     decimal(12,5)

  incerteza_orbita       varchar(10)
  codigo_condicao        varchar(10)
  rms                    decimal(10,6)
  referencia_mpc         varchar(50)
  num_observacoes        int
  num_oposicoes          int
  arco_anos              decimal(6,2)
  perturbacoes           varchar(100)
  computador_orbita      varchar(100)
  data_ultima_atualizacao datetime

  valido_de              datetime
  valido_ate             datetime
  solucao_atual          boolean
}

Table Aproximacao_Proxima {
  id_aproximacao_proxima int          [pk, increment]
  id_asteroide           int          [not null]          // FK -> Asteroide
  id_solucao_orbital     int                          // FK -> Solucao_Orbital, opcional
  datahora_aproximacao   datetime
  distancia_ua           decimal(13,10)
  distancia_ld           decimal(13,10)
  velocidade_relativa_kms decimal(10,4)
  critica                boolean
  datahora_registo       datetime
}

Table Prioridade_Alerta {
  id_prioridade_alerta   int          [pk, increment]
  codigo                 varchar(20)
  nome                   varchar(50)
  descricao              varchar(255)
}

Table Nivel_Alerta {
  id_nivel_alerta        int          [pk, increment]
  codigo                 int
  cor                    varchar(20)
  descricao              varchar(255)
  diametro_min_m         decimal(10,2)
  diametro_max_m         decimal(10,2)
  moid_min_ld            decimal(10,4)
  moid_max_ld            decimal(10,4)
  rms_maximo             decimal(10,4)
  janela_dias            int
}

Table Alerta {
  id_alerta              int          [pk, increment]
  id_asteroide           int          [not null]          // FK -> Asteroide
  id_solucao_orbital     int                          // FK -> Solucao_Orbital (0..1)
  id_aproximacao_proxima int                          // FK -> Aproximacao_Proxima (0..1)
  id_prioridade_alerta   int          [not null]          // FK -> Prioridade_Alerta
  id_nivel_alerta        int                          // FK -> Nivel_Alerta (0..1)

  codigo_regra           varchar(50)
  datahora_geracao       datetime
  ativo                  boolean
  titulo                 varchar(200)
  descricao              text
  datahora_reconhecimento datetime
  datahora_encerramento  datetime
}

Table Centro_Observacao {
  id_centro              int          [pk, increment]
  codigo                 varchar(20)
  nome                   varchar(100)
  pais                   varchar(50)
  cidade                 varchar(50)
  latitude_graus         decimal(9,6)
  longitude_graus        decimal(9,6)
  altitude_m             decimal(8,2)
}

Table Equipamento {
  id_equipamento         int          [pk, increment]
  id_centro              int          [not null]          // FK -> Centro_Observacao
  nome                   varchar(100)
  tipo                   varchar(50)
  modelo                 varchar(100)
  abertura_m             decimal(6,3)
  distancia_focal_m      decimal(6,3)
  notas                  text
}

Table Software {
  id_software            int          [pk, increment]
  nome                   varchar(100)
  versao                 varchar(50)
  fornecedor             varchar(100)
  tipo_licenca           varchar(50)
  website                varchar(200)
}

Table Astronomo {
  id_astronomo           int          [pk, increment]
  id_centro              int                          // FK -> Centro_Observacao (0..1)
  nome_completo          varchar(150)
  email                  varchar(150)
  telefone               varchar(30)
  funcao                 varchar(50)
}

Table Observacao {
  id_observacao          int          [pk, increment]
  id_asteroide           int          [not null]       // FK -> Asteroide
  id_astronomo           int          [not null]       // FK -> Astronomo
  id_equipamento         int          [not null]       // FK -> Equipamento
  id_software            int          [not null]       // FK -> Software

  datahora_observacao    datetime
  duracao_min            int
  modo                   varchar(50)
  seeing_arcseg          decimal(5,2)
  filtro                 varchar(20)
  magnitude              decimal(6,3)
  notas                  text
}

Table Imagem {
  id_imagem              int          [pk, increment]
  id_asteroide           int          [not null]       // FK -> Asteroide
  id_observacao          int                          // FK -> Observacao (0..1)

  nome_ficheiro          varchar(255)
  caminho_url            varchar(500)
  datahora_captura       datetime
  exposicao_s            decimal(8,3)
  filtro                 varchar(20)
  resolucao_x            int
  resolucao_y            int
}

//////////////////////////////////////////////////////
// Relações (Refs)
//////////////////////////////////////////////////////

Ref: Solucao_Orbital.id_asteroide > Asteroide.id_asteroide
Ref: Solucao_Orbital.codigo_classe > Classe_Orbital.codigo_classe

Ref: Aproximacao_Proxima.id_asteroide > Asteroide.id_asteroide
Ref: Aproximacao_Proxima.id_solucao_orbital > Solucao_Orbital.id_solucao_orbital

Ref: Alerta.id_asteroide > Asteroide.id_asteroide
Ref: Alerta.id_solucao_orbital > Solucao_Orbital.id_solucao_orbital
Ref: Alerta.id_aproximacao_proxima > Aproximacao_Proxima.id_aproximacao_proxima
Ref: Alerta.id_prioridade_alerta > Prioridade_Alerta.id_prioridade_alerta
Ref: Alerta.id_nivel_alerta > Nivel_Alerta.id_nivel_alerta

Ref: Equipamento.id_centro > Centro_Observacao.id_centro
Ref: Astronomo.id_centro > Centro_Observacao.id_centro

Ref: Observacao.id_asteroide > Asteroide.id_asteroide
Ref: Observacao.id_astronomo > Astronomo.id_astronomo
Ref: Observacao.id_equipamento > Equipamento.id_equipamento
Ref: Observacao.id_software > Software.id_software

Ref: Imagem.id_asteroide > Asteroide.id_asteroide
Ref: Imagem.id_observacao > Observacao.id_observacao
