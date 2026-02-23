-- ===============================
-- 지질[G]
-- ===============================

-- 암석[a]
INSERT INTO COMMON_CODE (CODE, CODE_NM, TOP_CD, TOP_CD_NM, MID_CD, MID_CD_NM, BOT_CD, BOT_CD_NM, RGSDE) VALUES
('Ga001','지판이동증거 암석','G','지질','Ga','암석','Ga001','지판이동증거 암석',datetime('now')),
('Ga002','지구내부 구성 암석','G','지질','Ga','암석','Ga002','지구내부 구성 암석',datetime('now')),
('Ga003','지질시대 대표 암석','G','지질','Ga','암석','Ga003','지질시대 대표 암석',datetime('now')),
('Ga004','외계기원','G','지질','Ga','암석','Ga004','외계기원',datetime('now'));

-- 층서[b]
INSERT INTO COMMON_CODE VALUES
(NULL,'Gb001','지질계통대표지질경계선','G','지질','Gb','층서','Gb001','지질계통대표지질경계선',NULL,datetime('now'));

-- 구조[c]
INSERT INTO COMMON_CODE (CODE, CODE_NM, TOP_CD, TOP_CD_NM, MID_CD, MID_CD_NM, BOT_CD, BOT_CD_NM, RGSDE) VALUES
('Gc001','퇴적작용','G','지질','Gc','구조','Gc001','퇴적작용',datetime('now')),
('Gc002','변형작용','G','지질','Gc','구조','Gc002','변형작용',datetime('now')),
('Gc003','변성작용','G','지질','Gc','구조','Gc003','변성작용',datetime('now')),
('Gc004','화성작용','G','지질','Gc','구조','Gc004','화성작용',datetime('now')),
('Gc005','생물작용','G','지질','Gc','구조','Gc005','생물작용',datetime('now'));


-- ===============================
-- 지형[L]
-- ===============================

-- 동굴[a]
INSERT INTO COMMON_CODE (CODE, CODE_NM, TOP_CD, TOP_CD_NM, MID_CD, MID_CD_NM, BOT_CD, BOT_CD_NM, RGSDE) VALUES
('La001','화산활동','L','지형','La','동굴','La001','화산활동',datetime('now')),
('La002','용식(석회암)작용','L','지형','La','동굴','La002','용식(석회암)작용',datetime('now')),
('La003','복합(화산+석회질, 용식+침식 등)','L','지형','La','동굴','La003','복합',datetime('now')),
('La004','침식작용','L','지형','La','동굴','La004','침식작용',datetime('now')),
('La005','기계적(구조)작용','L','지형','La','동굴','La005','기계적작용',datetime('now'));

-- 자연지형[b]
INSERT INTO COMMON_CODE (CODE, CODE_NM, TOP_CD, TOP_CD_NM, MID_CD, MID_CD_NM, BOT_CD, BOT_CD_NM, RGSDE) VALUES
('Lb001','구조운동','L','지형','Lb','자연지형','Lb001','구조운동',datetime('now')),
('Lb002','화산활동','L','지형','Lb','자연지형','Lb002','화산활동',datetime('now')),
('Lb003','침식/퇴적작용','L','지형','Lb','자연지형','Lb003','침식/퇴적작용',datetime('now')),
('Lb004','풍화작용','L','지형','Lb','자연지형','Lb004','풍화작용',datetime('now')),
('Lb005','착시','L','지형','Lb','자연지형','Lb005','착시',datetime('now'));


-- ===============================
-- 화석[F]
-- ===============================

-- 척추동물화석[a]
INSERT INTO COMMON_CODE (CODE, CODE_NM, TOP_CD, TOP_CD_NM, MID_CD, MID_CD_NM, BOT_CD, BOT_CD_NM, RGSDE) VALUES
('Fa001','어류','F','화석','Fa','척추동물화석','Fa001','어류',datetime('now')),
('Fa002','양서류','F','화석','Fa','척추동물화석','Fa002','양서류',datetime('now')),
('Fa003','파충류','F','화석','Fa','척추동물화석','Fa003','파충류',datetime('now')),
('Fa004','조류','F','화석','Fa','척추동물화석','Fa004','조류',datetime('now')),
('Fa005','포유류','F','화석','Fa','척추동물화석','Fa005','포유류',datetime('now'));

-- 무척추동물화석[b]
INSERT INTO COMMON_CODE (CODE, CODE_NM, TOP_CD, TOP_CD_NM, MID_CD, MID_CD_NM, BOT_CD, BOT_CD_NM, RGSDE) VALUES
('Fb001','연체동물','F','화석','Fb','무척추동물화석','Fb001','연체동물',datetime('now')),
('Fb002','절지동물','F','화석','Fb','무척추동물화석','Fb002','절지동물',datetime('now')),
('Fb003','완족동물','F','화석','Fb','무척추동물화석','Fb003','완족동물',datetime('now')),
('Fb004','극피동물','F','화석','Fb','무척추동물화석','Fb004','극피동물',datetime('now')),
('Fb005','자포/해면/태형동물','F','화석','Fb','무척추동물화석','Fb005','자포/해면/태형동물',datetime('now')),
('Fb006','반삭동물','F','화석','Fb','무척추동물화석','Fb006','반삭동물',datetime('now'));

-- 식물화석[c]
INSERT INTO COMMON_CODE VALUES
(NULL,'Fc001','양치식물','F','화석','Fc','식물화석','Fc001','양치식물',NULL,datetime('now')),
(NULL,'Fc002','나자식물','F','화석','Fc','식물화석','Fc002','나자식물',NULL,datetime('now')),
(NULL,'Fc003','현화식물','F','화석','Fc','식물화석','Fc003','현화식물',NULL,datetime('now')),
(NULL,'Fc004','선태식물','F','화석','Fc','식물화석','Fc004','선태식물',NULL,datetime('now'));

-- 생흔화석[d]
INSERT INTO COMMON_CODE VALUES
(NULL,'Fd001','생흔작용','F','화석','Fd','생흔화석','Fd001','생흔작용',NULL,datetime('now'));

-- 미화석[e]
INSERT INTO COMMON_CODE VALUES
(NULL,'Fe001','원생생물','F','화석','Fe','미화석','Fe001','원생생물',NULL,datetime('now')),
(NULL,'Fe002','동물미화석','F','화석','Fe','미화석','Fe002','동물미화석',NULL,datetime('now')),
(NULL,'Fe003','식물미화석','F','화석','Fe','미화석','Fe003','식물미화석',NULL,datetime('now'));


-- ===============================
-- 자연현상[N]
-- ===============================

INSERT INTO COMMON_CODE (CODE, CODE_NM, TOP_CD, TOP_CD_NM, MID_CD, MID_CD_NM, BOT_CD, BOT_CD_NM, RGSDE) VALUES
('Na001','바람작용','N','자연현상','Na','바람','Na001','바람작용',datetime('now')),
('Nb001','물/지하수작용','N','자연현상','Nb','물/지하수','Nb001','물/지하수작용',datetime('now')),
('Nc001','해양작용','N','자연현상','Nc','해양','Nc001','해양작용',datetime('now'));
