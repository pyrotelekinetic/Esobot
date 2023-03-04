import random
from collections import defaultdict
from typing import Union, Optional

import discord
from discord.ext import commands

from utils import get_pronouns, load_json, save_json
from constants.paths import ANON_SAVES


names = ['jan Aja', 'jan Aje', 'jan Ajo', 'jan Aju', 'jan Aka', 'jan Ake', 'jan Aki', 'jan Ako', 'jan Aku', 'jan Ala', 'jan Ale', 'jan Ali', 'jan Alo', 'jan Alu', 'jan Ama', 'jan Ame', 'jan Ami', 'jan Amo', 'jan Amu', 'jan Ana', 'jan Ane', 'jan Ani', 'jan Ano', 'jan Anu', 'jan Apa', 'jan Ape', 'jan Api', 'jan Apo', 'jan Apu', 'jan Asa', 'jan Ase', 'jan Asi', 'jan Aso', 'jan Asu', 'jan Ata', 'jan Ate', 'jan Ato', 'jan Atu', 'jan Eja', 'jan Eje', 'jan Ejo', 'jan Eju', 'jan Eka', 'jan Eke', 'jan Eki', 'jan Eko', 'jan Eku', 'jan Ela', 'jan Ele', 'jan Eli', 'jan Elo', 'jan Elu', 'jan Ema', 'jan Eme', 'jan Emi', 'jan Emo', 'jan Emu', 'jan Ena', 'jan Ene', 'jan Eni', 'jan Eno', 'jan Enu', 'jan Epa', 'jan Epe', 'jan Epi', 'jan Epo', 'jan Epu', 'jan Esa', 'jan Ese', 'jan Esi', 'jan Eso', 'jan Esu', 'jan Eta', 'jan Ete', 'jan Eto', 'jan Etu', 'jan Ija', 'jan Ije', 'jan Ijo', 'jan Iju', 'jan Ika', 'jan Iki', 'jan Iko', 'jan Iku', 'jan Ila', 'jan Ile', 'jan Ili', 'jan Ilo', 'jan Ilu', 'jan Ima', 'jan Ime', 'jan Imi', 'jan Imo', 'jan Imu', 'jan Ina', 'jan Ine', 'jan Ini', 'jan Ino', 'jan Inu', 'jan Ipa', 'jan Ipe', 'jan Ipi', 'jan Ipo', 'jan Ipu', 'jan Isa', 'jan Ise', 'jan Isi', 'jan Iso', 'jan Isu', 'jan Ita', 'jan Ite', 'jan Ito', 'jan Itu', 'jan Oja', 'jan Oje', 'jan Ojo', 'jan Oju', 'jan Oka', 'jan Oke', 'jan Oki', 'jan Oko', 'jan Oku', 'jan Ola', 'jan Ole', 'jan Oli', 'jan Olo', 'jan Olu', 'jan Oma', 'jan Ome', 'jan Omi', 'jan Omo', 'jan Omu', 'jan Ona', 'jan One', 'jan Oni', 'jan Ono', 'jan Onu', 'jan Opa', 'jan Ope', 'jan Opi', 'jan Opo', 'jan Opu', 'jan Osa', 'jan Ose', 'jan Osi', 'jan Oso', 'jan Osu', 'jan Ota', 'jan Ote', 'jan Oto', 'jan Otu', 'jan Uja', 'jan Uje', 'jan Ujo', 'jan Uju', 'jan Uka', 'jan Uke', 'jan Uki', 'jan Uko', 'jan Uku', 'jan Ula', 'jan Ule', 'jan Uli', 'jan Ulo', 'jan Ulu', 'jan Uma', 'jan Ume', 'jan Umi', 'jan Umo', 'jan Umu', 'jan Una', 'jan Une', 'jan Uni', 'jan Uno', 'jan Unu', 'jan Upa', 'jan Upe', 'jan Upi', 'jan Upo', 'jan Upu', 'jan Usa', 'jan Use', 'jan Usi', 'jan Uso', 'jan Usu', 'jan Uta', 'jan Ute', 'jan Uto', 'jan Utu', 'jan Anja', 'jan Anje', 'jan Anjo', 'jan Anju', 'jan Anka', 'jan Anke', 'jan Anki', 'jan Anko', 'jan Anku', 'jan Anla', 'jan Anle', 'jan Anli', 'jan Anlo', 'jan Anlu', 'jan Anpa', 'jan Anpe', 'jan Anpi', 'jan Anpo', 'jan Anpu', 'jan Ansa', 'jan Anse', 'jan Ansi', 'jan Anso', 'jan Ansu', 'jan Anta', 'jan Ante', 'jan Anto', 'jan Antu', 'jan Enja', 'jan Enje', 'jan Enjo', 'jan Enju', 'jan Enka', 'jan Enke', 'jan Enki', 'jan Enko', 'jan Enku', 'jan Enla', 'jan Enle', 'jan Enli', 'jan Enlo', 'jan Enlu', 'jan Enpa', 'jan Enpe', 'jan Enpi', 'jan Enpo', 'jan Enpu', 'jan Ensa', 'jan Ense', 'jan Ensi', 'jan Enso', 'jan Ensu', 'jan Enta', 'jan Ente', 'jan Ento', 'jan Entu', 'jan Inja', 'jan Inje', 'jan Injo', 'jan Inju', 'jan Inka', 'jan Inke', 'jan Inki', 'jan Inko', 'jan Inku', 'jan Inla', 'jan Inle', 'jan Inli', 'jan Inlo', 'jan Inlu', 'jan Inpa', 'jan Inpe', 'jan Inpi', 'jan Inpo', 'jan Inpu', 'jan Insa', 'jan Inse', 'jan Insi', 'jan Inso', 'jan Insu', 'jan Inta', 'jan Inte', 'jan Into', 'jan Intu', 'jan Jaja', 'jan Jaje', 'jan Jajo', 'jan Jaju', 'jan Jaka', 'jan Jake', 'jan Jaki', 'jan Jako', 'jan Jaku', 'jan Jala', 'jan Jale', 'jan Jali', 'jan Jalo', 'jan Jalu', 'jan Jama', 'jan Jame', 'jan Jami', 'jan Jamo', 'jan Jamu', 'jan Jana', 'jan Jane', 'jan Jani', 'jan Jano', 'jan Janu', 'jan Japa', 'jan Jape', 'jan Japi', 'jan Japo', 'jan Japu', 'jan Jasa', 'jan Jase', 'jan Jasi', 'jan Jaso', 'jan Jasu', 'jan Jata', 'jan Jate', 'jan Jato', 'jan Jatu', 'jan Jeja', 'jan Jeje', 'jan Jejo', 'jan Jeju', 'jan Jeka', 'jan Jeke', 'jan Jeki', 'jan Jeko', 'jan Jeku', 'jan Jela', 'jan Jele', 'jan Jeli', 'jan Jelo', 'jan Jelu', 'jan Jema', 'jan Jeme', 'jan Jemi', 'jan Jemo', 'jan Jemu', 'jan Jena', 'jan Jene', 'jan Jeni', 'jan Jeno', 'jan Jenu', 'jan Jepa', 'jan Jepe', 'jan Jepi', 'jan Jepo', 'jan Jepu', 'jan Jesa', 'jan Jese', 'jan Jesi', 'jan Jeso', 'jan Jesu', 'jan Jeta', 'jan Jete', 'jan Jeto', 'jan Jetu', 'jan Joja', 'jan Joje', 'jan Jojo', 'jan Joju', 'jan Joka', 'jan Joke', 'jan Joki', 'jan Joko', 'jan Joku', 'jan Jola', 'jan Jole', 'jan Joli', 'jan Jolo', 'jan Jolu', 'jan Joma', 'jan Jome', 'jan Jomi', 'jan Jomo', 'jan Jomu', 'jan Jona', 'jan Jone', 'jan Joni', 'jan Jono', 'jan Jonu', 'jan Jopa', 'jan Jope', 'jan Jopi', 'jan Jopo', 'jan Jopu', 'jan Josa', 'jan Jose', 'jan Josi', 'jan Joso', 'jan Josu', 'jan Jota', 'jan Jote', 'jan Joto', 'jan Jotu', 'jan Juja', 'jan Juje', 'jan Jujo', 'jan Juju', 'jan Juka', 'jan Juke', 'jan Juki', 'jan Juko', 'jan Juku', 'jan Jula', 'jan Jule', 'jan Juli', 'jan Julo', 'jan Julu', 'jan Juma', 'jan Jume', 'jan Jumi', 'jan Jumo', 'jan Jumu', 'jan Juna', 'jan June', 'jan Juni', 'jan Juno', 'jan Junu', 'jan Jupa', 'jan Jupe', 'jan Jupi', 'jan Jupo', 'jan Jupu', 'jan Jusa', 'jan Juse', 'jan Jusi', 'jan Juso', 'jan Jusu', 'jan Juta', 'jan Jute', 'jan Juto', 'jan Jutu', 'jan Kaja', 'jan Kaje', 'jan Kajo', 'jan Kaju', 'jan Kaka', 'jan Kake', 'jan Kaki', 'jan Kako', 'jan Kaku', 'jan Kala', 'jan Kale', 'jan Kali', 'jan Kalo', 'jan Kalu', 'jan Kama', 'jan Kame', 'jan Kami', 'jan Kamo', 'jan Kamu', 'jan Kana', 'jan Kane', 'jan Kani', 'jan Kano', 'jan Kanu', 'jan Kapa', 'jan Kape', 'jan Kapi', 'jan Kapo', 'jan Kapu', 'jan Kasa', 'jan Kase', 'jan Kasi', 'jan Kaso', 'jan Kasu', 'jan Kata', 'jan Kate', 'jan Kato', 'jan Katu', 'jan Keja', 'jan Keje', 'jan Kejo', 'jan Keju', 'jan Keka', 'jan Keke', 'jan Keki', 'jan Keko', 'jan Keku', 'jan Kela', 'jan Kele', 'jan Keli', 'jan Kelo', 'jan Kelu', 'jan Kema', 'jan Keme', 'jan Kemi', 'jan Kemo', 'jan Kemu', 'jan Kena', 'jan Kene', 'jan Keni', 'jan Keno', 'jan Kenu', 'jan Kepa', 'jan Kepe', 'jan Kepi', 'jan Kepo', 'jan Kepu', 'jan Kesa', 'jan Kese', 'jan Kesi', 'jan Keso', 'jan Kesu', 'jan Keta', 'jan Kete', 'jan Keto', 'jan Ketu', 'jan Kija', 'jan Kije', 'jan Kijo', 'jan Kiju', 'jan Kika', 'jan Kike', 'jan Kiki', 'jan Kiko', 'jan Kiku', 'jan Kila', 'jan Kile', 'jan Kili', 'jan Kilo', 'jan Kilu', 'jan Kima', 'jan Kime', 'jan Kimi', 'jan Kimo', 'jan Kimu', 'jan Kina', 'jan Kine', 'jan Kini', 'jan Kino', 'jan Kinu', 'jan Kipa', 'jan Kipe', 'jan Kipi', 'jan Kipo', 'jan Kipu', 'jan Kisa', 'jan Kise', 'jan Kisi', 'jan Kiso', 'jan Kisu', 'jan Kita', 'jan Kite', 'jan Kito', 'jan Kitu', 'jan Koja', 'jan Koje', 'jan Kojo', 'jan Koju', 'jan Koka', 'jan Koke', 'jan Koki', 'jan Koko', 'jan Koku', 'jan Kola', 'jan Kole', 'jan Koli', 'jan Kolo', 'jan Kolu', 'jan Koma', 'jan Kome', 'jan Komi', 'jan Komo', 'jan Komu', 'jan Kona', 'jan Kone', 'jan Koni', 'jan Kono', 'jan Konu', 'jan Kopa', 'jan Kope', 'jan Kopi', 'jan Kopo', 'jan Kopu', 'jan Kosa', 'jan Kose', 'jan Kosi', 'jan Koso', 'jan Kosu', 'jan Kota', 'jan Kote', 'jan Koto', 'jan Kotu', 'jan Kuja', 'jan Kuje', 'jan Kujo', 'jan Kuju', 'jan Kuka', 'jan Kuke', 'jan Kuki', 'jan Kuko', 'jan Kuku', 'jan Kula', 'jan Kule', 'jan Kuli', 'jan Kulo', 'jan Kulu', 'jan Kuma', 'jan Kume', 'jan Kumi', 'jan Kumo', 'jan Kumu', 'jan Kuna', 'jan Kune', 'jan Kuni', 'jan Kuno', 'jan Kunu', 'jan Kupa', 'jan Kupe', 'jan Kupi', 'jan Kupo', 'jan Kupu', 'jan Kusa', 'jan Kuse', 'jan Kusi', 'jan Kuso', 'jan Kusu', 'jan Kuta', 'jan Kute', 'jan Kuto', 'jan Kutu', 'jan Laja', 'jan Laje', 'jan Lajo', 'jan Laju', 'jan Laka', 'jan Lake', 'jan Laki', 'jan Lako', 'jan Laku', 'jan Lala', 'jan Lale', 'jan Lali', 'jan Lalo', 'jan Lalu', 'jan Lama', 'jan Lame', 'jan Lami', 'jan Lamo', 'jan Lamu', 'jan Lana', 'jan Lane', 'jan Lani', 'jan Lano', 'jan Lanu', 'jan Lapa', 'jan Lape', 'jan Lapi', 'jan Lapo', 'jan Lapu', 'jan Lasa', 'jan Lase', 'jan Lasi', 'jan Laso', 'jan Lasu', 'jan Lata', 'jan Late', 'jan Lato', 'jan Latu', 'jan Leja', 'jan Leje', 'jan Lejo', 'jan Leju', 'jan Leka', 'jan Leke', 'jan Leki', 'jan Leko', 'jan Leku', 'jan Lela', 'jan Lele', 'jan Leli', 'jan Lelo', 'jan Lelu', 'jan Lema', 'jan Leme', 'jan Lemi', 'jan Lemo', 'jan Lemu', 'jan Lena', 'jan Lene', 'jan Leni', 'jan Leno', 'jan Lenu', 'jan Lepa', 'jan Lepe', 'jan Lepi', 'jan Lepo', 'jan Lepu', 'jan Lesa', 'jan Lese', 'jan Lesi', 'jan Leso', 'jan Lesu', 'jan Leta', 'jan Lete', 'jan Leto', 'jan Letu', 'jan Lija', 'jan Lije', 'jan Lijo', 'jan Liju', 'jan Lika', 'jan Like', 'jan Liki', 'jan Liko', 'jan Liku', 'jan Lila', 'jan Lile', 'jan Lili', 'jan Lilo', 'jan Lilu', 'jan Lima', 'jan Lime', 'jan Limi', 'jan Limo', 'jan Limu', 'jan Lina', 'jan Line', 'jan Lini', 'jan Lino', 'jan Linu', 'jan Lipa', 'jan Lipe', 'jan Lipi', 'jan Lipo', 'jan Lipu', 'jan Lisa', 'jan Lise', 'jan Lisi', 'jan Liso', 'jan Lisu', 'jan Lita', 'jan Lite', 'jan Lito', 'jan Litu', 'jan Loja', 'jan Loje', 'jan Lojo', 'jan Loju', 'jan Loka', 'jan Loke', 'jan Loki', 'jan Loko', 'jan Loku', 'jan Lola', 'jan Lole', 'jan Loli', 'jan Lolo', 'jan Lolu', 'jan Loma', 'jan Lome', 'jan Lomi', 'jan Lomo', 'jan Lomu', 'jan Lona', 'jan Lone', 'jan Loni', 'jan Lono', 'jan Lonu', 'jan Lopa', 'jan Lope', 'jan Lopi', 'jan Lopo', 'jan Lopu', 'jan Losa', 'jan Lose', 'jan Losi', 'jan Loso', 'jan Losu', 'jan Lota', 'jan Lote', 'jan Loto', 'jan Lotu', 'jan Luja', 'jan Luje', 'jan Lujo', 'jan Luju', 'jan Luka', 'jan Luke', 'jan Luki', 'jan Luko', 'jan Luku', 'jan Lula', 'jan Lule', 'jan Luli', 'jan Lulo', 'jan Lulu', 'jan Luma', 'jan Lume', 'jan Lumi', 'jan Lumo', 'jan Lumu', 'jan Luna', 'jan Lune', 'jan Luni', 'jan Luno', 'jan Lunu', 'jan Lupa', 'jan Lupe', 'jan Lupi', 'jan Lupo', 'jan Lupu', 'jan Lusa', 'jan Luse', 'jan Lusi', 'jan Luso', 'jan Lusu', 'jan Luta', 'jan Lute', 'jan Luto', 'jan Lutu', 'jan Maja', 'jan Maje', 'jan Majo', 'jan Maju', 'jan Maka', 'jan Make', 'jan Maki', 'jan Mako', 'jan Maku', 'jan Mala', 'jan Male', 'jan Mali', 'jan Malo', 'jan Malu', 'jan Mama', 'jan Mame', 'jan Mami', 'jan Mamo', 'jan Mamu', 'jan Mana', 'jan Mane', 'jan Mani', 'jan Mano', 'jan Manu', 'jan Mapa', 'jan Mape', 'jan Mapi', 'jan Mapo', 'jan Mapu', 'jan Masa', 'jan Mase', 'jan Masi', 'jan Maso', 'jan Masu', 'jan Mata', 'jan Mate', 'jan Mato', 'jan Matu', 'jan Meja', 'jan Meje', 'jan Mejo', 'jan Meju', 'jan Meka', 'jan Meke', 'jan Meki', 'jan Meko', 'jan Meku', 'jan Mela', 'jan Mele', 'jan Meli', 'jan Melo', 'jan Melu', 'jan Mema', 'jan Meme', 'jan Memi', 'jan Memo', 'jan Memu', 'jan Mena', 'jan Mene', 'jan Meni', 'jan Meno', 'jan Menu', 'jan Mepa', 'jan Mepe', 'jan Mepi', 'jan Mepo', 'jan Mepu', 'jan Mesa', 'jan Mese', 'jan Mesi', 'jan Meso', 'jan Mesu', 'jan Meta', 'jan Mete', 'jan Meto', 'jan Metu', 'jan Mija', 'jan Mije', 'jan Mijo', 'jan Miju', 'jan Mika', 'jan Mike', 'jan Miki', 'jan Miko', 'jan Miku', 'jan Mila', 'jan Mile', 'jan Mili', 'jan Milo', 'jan Milu', 'jan Mima', 'jan Mime', 'jan Mimi', 'jan Mimo', 'jan Mimu', 'jan Mina', 'jan Mine', 'jan Mini', 'jan Mino', 'jan Minu', 'jan Mipa', 'jan Mipe', 'jan Mipi', 'jan Mipo', 'jan Mipu', 'jan Misa', 'jan Mise', 'jan Misi', 'jan Miso', 'jan Misu', 'jan Mita', 'jan Mite', 'jan Mito', 'jan Mitu', 'jan Moja', 'jan Moje', 'jan Mojo', 'jan Moju', 'jan Moka', 'jan Moke', 'jan Moki', 'jan Moko', 'jan Moku', 'jan Mola', 'jan Mole', 'jan Moli', 'jan Molo', 'jan Molu', 'jan Moma', 'jan Mome', 'jan Momi', 'jan Momo', 'jan Momu', 'jan Mona', 'jan Mone', 'jan Moni', 'jan Mono', 'jan Monu', 'jan Mopa', 'jan Mope', 'jan Mopi', 'jan Mopo', 'jan Mopu', 'jan Mosa', 'jan Mose', 'jan Mosi', 'jan Moso', 'jan Mosu', 'jan Mota', 'jan Mote', 'jan Moto', 'jan Motu', 'jan Muja', 'jan Muje', 'jan Mujo', 'jan Muju', 'jan Muka', 'jan Muke', 'jan Muki', 'jan Muko', 'jan Muku', 'jan Mula', 'jan Mule', 'jan Muli', 'jan Mulo', 'jan Mulu', 'jan Muma', 'jan Mume', 'jan Mumi', 'jan Mumo', 'jan Mumu', 'jan Muna', 'jan Mune', 'jan Muni', 'jan Muno', 'jan Munu', 'jan Mupa', 'jan Mupe', 'jan Mupi', 'jan Mupo', 'jan Mupu', 'jan Musa', 'jan Muse', 'jan Musi', 'jan Muso', 'jan Musu', 'jan Muta', 'jan Mute', 'jan Muto', 'jan Mutu', 'jan Naja', 'jan Naje', 'jan Najo', 'jan Naju', 'jan Naka', 'jan Nake', 'jan Naki', 'jan Nako', 'jan Naku', 'jan Nala', 'jan Nale', 'jan Nali', 'jan Nalo', 'jan Nalu', 'jan Nama', 'jan Name', 'jan Nami', 'jan Namo', 'jan Namu', 'jan Nana', 'jan Nane', 'jan Nani', 'jan Nano', 'jan Nanu', 'jan Napa', 'jan Nape', 'jan Napi', 'jan Napo', 'jan Napu', 'jan Nasa', 'jan Nase', 'jan Nasi', 'jan Naso', 'jan Nasu', 'jan Nata', 'jan Nate', 'jan Nato', 'jan Natu', 'jan Neja', 'jan Neje', 'jan Nejo', 'jan Neju', 'jan Neka', 'jan Neke', 'jan Neki', 'jan Neko', 'jan Neku', 'jan Nela', 'jan Nele', 'jan Neli', 'jan Nelo', 'jan Nelu', 'jan Nema', 'jan Neme', 'jan Nemi', 'jan Nemo', 'jan Nemu', 'jan Nena', 'jan Nene', 'jan Neni', 'jan Neno', 'jan Nenu', 'jan Nepa', 'jan Nepe', 'jan Nepi', 'jan Nepo', 'jan Nepu', 'jan Nesa', 'jan Nese', 'jan Nesi', 'jan Neso', 'jan Nesu', 'jan Neta', 'jan Nete', 'jan Neto', 'jan Netu', 'jan Nija', 'jan Nije', 'jan Nijo', 'jan Niju', 'jan Nika', 'jan Nike', 'jan Niki', 'jan Niko', 'jan Niku', 'jan Nila', 'jan Nile', 'jan Nili', 'jan Nilo', 'jan Nilu', 'jan Nima', 'jan Nime', 'jan Nimi', 'jan Nimo', 'jan Nimu', 'jan Nina', 'jan Nine', 'jan Nini', 'jan Nino', 'jan Ninu', 'jan Nipa', 'jan Nipe', 'jan Nipi', 'jan Nipo', 'jan Nipu', 'jan Nisa', 'jan Nise', 'jan Nisi', 'jan Niso', 'jan Nisu', 'jan Nita', 'jan Nite', 'jan Nito', 'jan Nitu', 'jan Noja', 'jan Noje', 'jan Nojo', 'jan Noju', 'jan Noka', 'jan Noke', 'jan Noki', 'jan Noko', 'jan Noku', 'jan Nola', 'jan Nole', 'jan Noli', 'jan Nolo', 'jan Nolu', 'jan Noma', 'jan Nome', 'jan Nomi', 'jan Nomo', 'jan Nomu', 'jan Nona', 'jan None', 'jan Noni', 'jan Nono', 'jan Nonu', 'jan Nopa', 'jan Nope', 'jan Nopi', 'jan Nopo', 'jan Nopu', 'jan Nosa', 'jan Nose', 'jan Nosi', 'jan Noso', 'jan Nosu', 'jan Nota', 'jan Note', 'jan Noto', 'jan Notu', 'jan Nuja', 'jan Nuje', 'jan Nujo', 'jan Nuju', 'jan Nuka', 'jan Nuke', 'jan Nuki', 'jan Nuko', 'jan Nuku', 'jan Nula', 'jan Nule', 'jan Nuli', 'jan Nulo', 'jan Nulu', 'jan Numa', 'jan Nume', 'jan Numi', 'jan Numo', 'jan Numu', 'jan Nuna', 'jan Nune', 'jan Nuni', 'jan Nuno', 'jan Nunu', 'jan Nupa', 'jan Nupe', 'jan Nupi', 'jan Nupo', 'jan Nupu', 'jan Nusa', 'jan Nuse', 'jan Nusi', 'jan Nuso', 'jan Nusu', 'jan Nuta', 'jan Nute', 'jan Nuto', 'jan Nutu', 'jan Onja', 'jan Onje', 'jan Onjo', 'jan Onju', 'jan Onka', 'jan Onke', 'jan Onki', 'jan Onko', 'jan Onku', 'jan Onla', 'jan Onle', 'jan Onli', 'jan Onlo', 'jan Onlu', 'jan Onpa', 'jan Onpe', 'jan Onpi', 'jan Onpo', 'jan Onpu', 'jan Onsa', 'jan Onse', 'jan Onsi', 'jan Onso', 'jan Onsu', 'jan Onta', 'jan Onte', 'jan Onto', 'jan Ontu', 'jan Paja', 'jan Paje', 'jan Pajo', 'jan Paju', 'jan Paka', 'jan Pake', 'jan Paki', 'jan Pako', 'jan Paku', 'jan Pala', 'jan Pale', 'jan Pali', 'jan Palo', 'jan Palu', 'jan Pama', 'jan Pame', 'jan Pami', 'jan Pamo', 'jan Pamu', 'jan Pana', 'jan Pane', 'jan Pani', 'jan Pano', 'jan Panu', 'jan Papa', 'jan Pape', 'jan Papi', 'jan Papo', 'jan Papu', 'jan Pasa', 'jan Pase', 'jan Pasi', 'jan Paso', 'jan Pasu', 'jan Pata', 'jan Pate', 'jan Pato', 'jan Patu', 'jan Peja', 'jan Peje', 'jan Pejo', 'jan Peju', 'jan Peka', 'jan Peke', 'jan Peki', 'jan Peko', 'jan Peku', 'jan Pela', 'jan Pele', 'jan Peli', 'jan Pelo', 'jan Pelu', 'jan Pema', 'jan Peme', 'jan Pemi', 'jan Pemo', 'jan Pemu', 'jan Pena', 'jan Pene', 'jan Peni', 'jan Peno', 'jan Penu', 'jan Pepa', 'jan Pepe', 'jan Pepi', 'jan Pepo', 'jan Pepu', 'jan Pesa', 'jan Pese', 'jan Pesi', 'jan Peso', 'jan Pesu', 'jan Peta', 'jan Pete', 'jan Peto', 'jan Petu', 'jan Pija', 'jan Pije', 'jan Pijo', 'jan Piju', 'jan Pika', 'jan Pike', 'jan Piki', 'jan Piko', 'jan Piku', 'jan Pila', 'jan Pile', 'jan Pili', 'jan Pilo', 'jan Pilu', 'jan Pima', 'jan Pime', 'jan Pimi', 'jan Pimo', 'jan Pimu', 'jan Pina', 'jan Pine', 'jan Pini', 'jan Pino', 'jan Pinu', 'jan Pipa', 'jan Pipe', 'jan Pipi', 'jan Pipo', 'jan Pipu', 'jan Pisa', 'jan Pise', 'jan Pisi', 'jan Piso', 'jan Pisu', 'jan Pita', 'jan Pite', 'jan Pito', 'jan Pitu', 'jan Poja', 'jan Poje', 'jan Pojo', 'jan Poju', 'jan Poka', 'jan Poke', 'jan Poki', 'jan Poko', 'jan Poku', 'jan Pola', 'jan Pole', 'jan Poli', 'jan Polo', 'jan Polu', 'jan Poma', 'jan Pome', 'jan Pomi', 'jan Pomo', 'jan Pomu', 'jan Pona', 'jan Pone', 'jan Poni', 'jan Pono', 'jan Ponu', 'jan Popa', 'jan Pope', 'jan Popi', 'jan Popo', 'jan Popu', 'jan Posa', 'jan Pose', 'jan Posi', 'jan Poso', 'jan Posu', 'jan Pota', 'jan Pote', 'jan Poto', 'jan Potu', 'jan Puja', 'jan Puje', 'jan Pujo', 'jan Puju', 'jan Puka', 'jan Puke', 'jan Puki', 'jan Puko', 'jan Puku', 'jan Pula', 'jan Pule', 'jan Puli', 'jan Pulo', 'jan Pulu', 'jan Puma', 'jan Pume', 'jan Pumi', 'jan Pumo', 'jan Pumu', 'jan Puna', 'jan Pune', 'jan Puni', 'jan Puno', 'jan Punu', 'jan Pupa', 'jan Pupe', 'jan Pupi', 'jan Pupo', 'jan Pupu', 'jan Pusa', 'jan Puse', 'jan Pusi', 'jan Puso', 'jan Pusu', 'jan Puta', 'jan Pute', 'jan Puto', 'jan Putu', 'jan Saja', 'jan Saje', 'jan Sajo', 'jan Saju', 'jan Saka', 'jan Sake', 'jan Saki', 'jan Sako', 'jan Saku', 'jan Sala', 'jan Sale', 'jan Sali', 'jan Salo', 'jan Salu', 'jan Sama', 'jan Same', 'jan Sami', 'jan Samo', 'jan Samu', 'jan Sana', 'jan Sane', 'jan Sani', 'jan Sano', 'jan Sanu', 'jan Sapa', 'jan Sape', 'jan Sapi', 'jan Sapo', 'jan Sapu', 'jan Sasa', 'jan Sase', 'jan Sasi', 'jan Saso', 'jan Sasu', 'jan Sata', 'jan Sate', 'jan Sato', 'jan Satu', 'jan Seja', 'jan Seje', 'jan Sejo', 'jan Seju', 'jan Seka', 'jan Seke', 'jan Seki', 'jan Seko', 'jan Seku', 'jan Sela', 'jan Sele', 'jan Seli', 'jan Selo', 'jan Selu', 'jan Sema', 'jan Seme', 'jan Semi', 'jan Semo', 'jan Semu', 'jan Sena', 'jan Sene', 'jan Seni', 'jan Seno', 'jan Senu', 'jan Sepa', 'jan Sepe', 'jan Sepi', 'jan Sepo', 'jan Sepu', 'jan Sesa', 'jan Sese', 'jan Sesi', 'jan Seso', 'jan Sesu', 'jan Seta', 'jan Sete', 'jan Seto', 'jan Setu', 'jan Sija', 'jan Sije', 'jan Sijo', 'jan Siju', 'jan Sika', 'jan Sike', 'jan Siki', 'jan Siko', 'jan Siku', 'jan Sila', 'jan Sile', 'jan Sili', 'jan Silo', 'jan Silu', 'jan Sima', 'jan Sime', 'jan Simi', 'jan Simo', 'jan Simu', 'jan Sina', 'jan Sine', 'jan Sini', 'jan Sino', 'jan Sinu', 'jan Sipa', 'jan Sipe', 'jan Sipi', 'jan Sipo', 'jan Sipu', 'jan Sisa', 'jan Sise', 'jan Sisi', 'jan Siso', 'jan Sisu', 'jan Sita', 'jan Site', 'jan Sito', 'jan Situ', 'jan Soja', 'jan Soje', 'jan Sojo', 'jan Soju', 'jan Soka', 'jan Soke', 'jan Soki', 'jan Soko', 'jan Soku', 'jan Sola', 'jan Sole', 'jan Soli', 'jan Solo', 'jan Solu', 'jan Soma', 'jan Some', 'jan Somi', 'jan Somo', 'jan Somu', 'jan Sona', 'jan Sone', 'jan Soni', 'jan Sono', 'jan Sonu', 'jan Sopa', 'jan Sope', 'jan Sopi', 'jan Sopo', 'jan Sopu', 'jan Sosa', 'jan Sose', 'jan Sosi', 'jan Soso', 'jan Sosu', 'jan Sota', 'jan Sote', 'jan Soto', 'jan Sotu', 'jan Suja', 'jan Suje', 'jan Sujo', 'jan Suju', 'jan Suka', 'jan Suke', 'jan Suki', 'jan Suko', 'jan Suku', 'jan Sula', 'jan Sule', 'jan Suli', 'jan Sulo', 'jan Sulu', 'jan Suma', 'jan Sume', 'jan Sumi', 'jan Sumo', 'jan Sumu', 'jan Suna', 'jan Sune', 'jan Suni', 'jan Suno', 'jan Sunu', 'jan Supa', 'jan Supe', 'jan Supi', 'jan Supo', 'jan Supu', 'jan Susa', 'jan Suse', 'jan Susi', 'jan Suso', 'jan Susu', 'jan Suta', 'jan Sute', 'jan Suto', 'jan Sutu', 'jan Taja', 'jan Taje', 'jan Tajo', 'jan Taju', 'jan Taka', 'jan Take', 'jan Taki', 'jan Tako', 'jan Taku', 'jan Tala', 'jan Tale', 'jan Tali', 'jan Talo', 'jan Talu', 'jan Tama', 'jan Tame', 'jan Tami', 'jan Tamo', 'jan Tamu', 'jan Tana', 'jan Tane', 'jan Tani', 'jan Tano', 'jan Tanu', 'jan Tapa', 'jan Tape', 'jan Tapi', 'jan Tapo', 'jan Tapu', 'jan Tasa', 'jan Tase', 'jan Tasi', 'jan Taso', 'jan Tasu', 'jan Tata', 'jan Tate', 'jan Tato', 'jan Tatu', 'jan Teja', 'jan Teje', 'jan Tejo', 'jan Teju', 'jan Teka', 'jan Teke', 'jan Teki', 'jan Teko', 'jan Teku', 'jan Tela', 'jan Tele', 'jan Teli', 'jan Telo', 'jan Telu', 'jan Tema', 'jan Teme', 'jan Temi', 'jan Temo', 'jan Temu', 'jan Tena', 'jan Tene', 'jan Teni', 'jan Teno', 'jan Tenu', 'jan Tepa', 'jan Tepe', 'jan Tepi', 'jan Tepo', 'jan Tepu', 'jan Tesa', 'jan Tese', 'jan Tesi', 'jan Teso', 'jan Tesu', 'jan Teta', 'jan Tete', 'jan Teto', 'jan Tetu', 'jan Toja', 'jan Toje', 'jan Tojo', 'jan Toju', 'jan Toka', 'jan Toke', 'jan Toki', 'jan Toko', 'jan Toku', 'jan Tola', 'jan Tole', 'jan Toli', 'jan Tolo', 'jan Tolu', 'jan Toma', 'jan Tome', 'jan Tomi', 'jan Tomo', 'jan Tomu', 'jan Tona', 'jan Tone', 'jan Toni', 'jan Tono', 'jan Tonu', 'jan Topa', 'jan Tope', 'jan Topi', 'jan Topo', 'jan Topu', 'jan Tosa', 'jan Tose', 'jan Tosi', 'jan Toso', 'jan Tosu', 'jan Tota', 'jan Tote', 'jan Toto', 'jan Totu', 'jan Tuja', 'jan Tuje', 'jan Tujo', 'jan Tuju', 'jan Tuka', 'jan Tuke', 'jan Tuki', 'jan Tuko', 'jan Tuku', 'jan Tula', 'jan Tule', 'jan Tuli', 'jan Tulo', 'jan Tulu', 'jan Tuma', 'jan Tume', 'jan Tumi', 'jan Tumo', 'jan Tumu', 'jan Tuna', 'jan Tune', 'jan Tuni', 'jan Tuno', 'jan Tunu', 'jan Tupa', 'jan Tupe', 'jan Tupi', 'jan Tupo', 'jan Tupu', 'jan Tusa', 'jan Tuse', 'jan Tusi', 'jan Tuso', 'jan Tusu', 'jan Tuta', 'jan Tute', 'jan Tuto', 'jan Tutu', 'jan Unja', 'jan Unje', 'jan Unjo', 'jan Unju', 'jan Unka', 'jan Unke', 'jan Unki', 'jan Unko', 'jan Unku', 'jan Unla', 'jan Unle', 'jan Unli', 'jan Unlo', 'jan Unlu', 'jan Unpe', 'jan Unpi', 'jan Unpo', 'jan Unpu', 'jan Unsa', 'jan Unse', 'jan Unsi', 'jan Unso', 'jan Unsu', 'jan Unta', 'jan Unte', 'jan Unto', 'jan Untu', 'jan Waja', 'jan Waje', 'jan Wajo', 'jan Waju', 'jan Waka', 'jan Wake', 'jan Waki', 'jan Wako', 'jan Waku', 'jan Wala', 'jan Wale', 'jan Wali', 'jan Walo', 'jan Walu', 'jan Wama', 'jan Wame', 'jan Wami', 'jan Wamo', 'jan Wamu', 'jan Wana', 'jan Wane', 'jan Wani', 'jan Wano', 'jan Wanu', 'jan Wapa', 'jan Wape', 'jan Wapi', 'jan Wapo', 'jan Wapu', 'jan Wasa', 'jan Wase', 'jan Wasi', 'jan Waso', 'jan Wasu', 'jan Wata', 'jan Wate', 'jan Wato', 'jan Watu', 'jan Weja', 'jan Weje', 'jan Wejo', 'jan Weju', 'jan Weka', 'jan Weke', 'jan Weki', 'jan Weko', 'jan Weku', 'jan Wela', 'jan Wele', 'jan Weli', 'jan Welo', 'jan Welu', 'jan Wema', 'jan Weme', 'jan Wemi', 'jan Wemo', 'jan Wemu', 'jan Wena', 'jan Wene', 'jan Weni', 'jan Weno', 'jan Wenu', 'jan Wepa', 'jan Wepe', 'jan Wepi', 'jan Wepo', 'jan Wepu', 'jan Wesa', 'jan Wese', 'jan Wesi', 'jan Weso', 'jan Wesu', 'jan Weta', 'jan Wete', 'jan Weto', 'jan Wetu', 'jan Wija', 'jan Wije', 'jan Wijo', 'jan Wiju', 'jan Wika', 'jan Wike', 'jan Wiki', 'jan Wiko', 'jan Wiku', 'jan Wila', 'jan Wile', 'jan Wili', 'jan Wilo', 'jan Wilu', 'jan Wima', 'jan Wime', 'jan Wimi', 'jan Wimo', 'jan Wimu', 'jan Wina', 'jan Wine', 'jan Wini', 'jan Wino', 'jan Winu', 'jan Wipa', 'jan Wipe', 'jan Wipi', 'jan Wipo', 'jan Wipu', 'jan Wisa', 'jan Wise', 'jan Wisi', 'jan Wiso', 'jan Wisu', 'jan Wita', 'jan Wite', 'jan Wito', 'jan Witu', 'jan Janja', 'jan Janje', 'jan Janjo', 'jan Janju', 'jan Janka', 'jan Janke', 'jan Janki', 'jan Janko', 'jan Janku', 'jan Janla', 'jan Janle', 'jan Janli', 'jan Janlo', 'jan Janlu', 'jan Janpa', 'jan Janpe', 'jan Janpi', 'jan Janpo', 'jan Janpu', 'jan Jansa', 'jan Janse', 'jan Jansi', 'jan Janso', 'jan Jansu', 'jan Janta', 'jan Jante', 'jan Janto', 'jan Jantu', 'jan Jenja', 'jan Jenje', 'jan Jenjo', 'jan Jenju', 'jan Jenka', 'jan Jenke', 'jan Jenki', 'jan Jenko', 'jan Jenku', 'jan Jenla', 'jan Jenle', 'jan Jenli', 'jan Jenlo', 'jan Jenlu', 'jan Jenpa', 'jan Jenpe', 'jan Jenpi', 'jan Jenpo', 'jan Jenpu', 'jan Jensa', 'jan Jense', 'jan Jensi', 'jan Jenso', 'jan Jensu', 'jan Jenta', 'jan Jente', 'jan Jento', 'jan Jentu', 'jan Jonja', 'jan Jonje', 'jan Jonjo', 'jan Jonju', 'jan Jonka', 'jan Jonke', 'jan Jonki', 'jan Jonko', 'jan Jonku', 'jan Jonla', 'jan Jonle', 'jan Jonli', 'jan Jonlo', 'jan Jonlu', 'jan Jonpa', 'jan Jonpe', 'jan Jonpi', 'jan Jonpo', 'jan Jonpu', 'jan Jonsa', 'jan Jonse', 'jan Jonsi', 'jan Jonso', 'jan Jonsu', 'jan Jonta', 'jan Jonte', 'jan Jonto', 'jan Jontu', 'jan Junja', 'jan Junje', 'jan Junjo', 'jan Junju', 'jan Junka', 'jan Junke', 'jan Junki', 'jan Junko', 'jan Junku', 'jan Junla', 'jan Junle', 'jan Junli', 'jan Junlo', 'jan Junlu', 'jan Junpa', 'jan Junpe', 'jan Junpi', 'jan Junpo', 'jan Junpu', 'jan Junsa', 'jan Junse', 'jan Junsi', 'jan Junso', 'jan Junsu', 'jan Junta', 'jan Junte', 'jan Junto', 'jan Juntu', 'jan Kanja', 'jan Kanje', 'jan Kanjo', 'jan Kanju', 'jan Kanka', 'jan Kanke', 'jan Kanki', 'jan Kanko', 'jan Kanku', 'jan Kanla', 'jan Kanle', 'jan Kanli', 'jan Kanlo', 'jan Kanlu', 'jan Kanpa', 'jan Kanpe', 'jan Kanpi', 'jan Kanpo', 'jan Kanpu', 'jan Kansa', 'jan Kanse', 'jan Kansi', 'jan Kanso', 'jan Kansu', 'jan Kanta', 'jan Kante', 'jan Kanto', 'jan Kantu', 'jan Kenja', 'jan Kenje', 'jan Kenjo', 'jan Kenju', 'jan Kenka', 'jan Kenke', 'jan Kenki', 'jan Kenko', 'jan Kenku', 'jan Kenla', 'jan Kenle', 'jan Kenli', 'jan Kenlo', 'jan Kenlu', 'jan Kenpa', 'jan Kenpe', 'jan Kenpi', 'jan Kenpo', 'jan Kenpu', 'jan Kensa', 'jan Kense', 'jan Kensi', 'jan Kenso', 'jan Kensu', 'jan Kenta', 'jan Kente', 'jan Kento', 'jan Kentu', 'jan Kinja', 'jan Kinje', 'jan Kinjo', 'jan Kinju', 'jan Kinka', 'jan Kinke', 'jan Kinki', 'jan Kinko', 'jan Kinku', 'jan Kinla', 'jan Kinle', 'jan Kinli', 'jan Kinlo', 'jan Kinlu', 'jan Kinpa', 'jan Kinpe', 'jan Kinpi', 'jan Kinpo', 'jan Kinpu', 'jan Kinsa', 'jan Kinse', 'jan Kinsi', 'jan Kinso', 'jan Kinsu', 'jan Kinta', 'jan Kinte', 'jan Kinto', 'jan Kintu', 'jan Konja', 'jan Konje', 'jan Konjo', 'jan Konju', 'jan Konka', 'jan Konke', 'jan Konki', 'jan Konko', 'jan Konku', 'jan Konla', 'jan Konle', 'jan Konli', 'jan Konlo', 'jan Konlu', 'jan Konpa', 'jan Konpe', 'jan Konpi', 'jan Konpo', 'jan Konpu', 'jan Konsa', 'jan Konse', 'jan Konsi', 'jan Konso', 'jan Konsu', 'jan Konta', 'jan Konte', 'jan Konto', 'jan Kontu', 'jan Kunja', 'jan Kunje', 'jan Kunjo', 'jan Kunju', 'jan Kunka', 'jan Kunke', 'jan Kunki', 'jan Kunko', 'jan Kunku', 'jan Kunla', 'jan Kunle', 'jan Kunli', 'jan Kunlo', 'jan Kunlu', 'jan Kunpa', 'jan Kunpe', 'jan Kunpi', 'jan Kunpo', 'jan Kunpu', 'jan Kunsa', 'jan Kunse', 'jan Kunsi', 'jan Kunso', 'jan Kunsu', 'jan Kunta', 'jan Kunte', 'jan Kunto', 'jan Kuntu', 'jan Lanja', 'jan Lanje', 'jan Lanjo', 'jan Lanju', 'jan Lanka', 'jan Lanke', 'jan Lanki', 'jan Lanko', 'jan Lanku', 'jan Lanla', 'jan Lanle', 'jan Lanli', 'jan Lanlo', 'jan Lanlu', 'jan Lanpa', 'jan Lanpe', 'jan Lanpi', 'jan Lanpo', 'jan Lanpu', 'jan Lansa', 'jan Lanse', 'jan Lansi', 'jan Lanso', 'jan Lansu', 'jan Lanta', 'jan Lante', 'jan Lanto', 'jan Lantu', 'jan Lenja', 'jan Lenje', 'jan Lenjo', 'jan Lenju', 'jan Lenka', 'jan Lenke', 'jan Lenki', 'jan Lenko', 'jan Lenku', 'jan Lenla', 'jan Lenle', 'jan Lenli', 'jan Lenlo', 'jan Lenlu', 'jan Lenpa', 'jan Lenpe', 'jan Lenpi', 'jan Lenpo', 'jan Lenpu', 'jan Lensa', 'jan Lense', 'jan Lensi', 'jan Lenso', 'jan Lensu', 'jan Lenta', 'jan Lente', 'jan Lento', 'jan Lentu', 'jan Linja', 'jan Linje', 'jan Linjo', 'jan Linju', 'jan Linka', 'jan Linke', 'jan Linki', 'jan Linko', 'jan Linku', 'jan Linla', 'jan Linle', 'jan Linli', 'jan Linlo', 'jan Linlu', 'jan Linpa', 'jan Linpe', 'jan Linpi', 'jan Linpo', 'jan Linpu', 'jan Linsa', 'jan Linse', 'jan Linsi', 'jan Linso', 'jan Linsu', 'jan Linta', 'jan Linte', 'jan Linto', 'jan Lintu', 'jan Lonja', 'jan Lonje', 'jan Lonjo', 'jan Lonju', 'jan Lonka', 'jan Lonke', 'jan Lonki', 'jan Lonko', 'jan Lonku', 'jan Lonla', 'jan Lonle', 'jan Lonli', 'jan Lonlo', 'jan Lonlu', 'jan Lonpa', 'jan Lonpe', 'jan Lonpi', 'jan Lonpo', 'jan Lonpu', 'jan Lonsa', 'jan Lonse', 'jan Lonsi', 'jan Lonso', 'jan Lonsu', 'jan Lonta', 'jan Lonte', 'jan Lonto', 'jan Lontu', 'jan Lunja', 'jan Lunje', 'jan Lunjo', 'jan Lunju', 'jan Lunka', 'jan Lunke', 'jan Lunki', 'jan Lunko', 'jan Lunku', 'jan Lunla', 'jan Lunle', 'jan Lunli', 'jan Lunlo', 'jan Lunlu', 'jan Lunpa', 'jan Lunpe', 'jan Lunpi', 'jan Lunpo', 'jan Lunpu', 'jan Lunsa', 'jan Lunse', 'jan Lunsi', 'jan Lunso', 'jan Lunsu', 'jan Lunta', 'jan Lunte', 'jan Lunto', 'jan Luntu', 'jan Manja', 'jan Manje', 'jan Manjo', 'jan Manju', 'jan Manka', 'jan Manke', 'jan Manki', 'jan Manko', 'jan Manku', 'jan Manla', 'jan Manle', 'jan Manli', 'jan Manlo', 'jan Manlu', 'jan Manpa', 'jan Manpe', 'jan Manpi', 'jan Manpo', 'jan Manpu', 'jan Mansa', 'jan Manse', 'jan Mansi', 'jan Manso', 'jan Mansu', 'jan Manta', 'jan Mante', 'jan Manto', 'jan Mantu', 'jan Menja', 'jan Menje', 'jan Menjo', 'jan Menju', 'jan Menka', 'jan Menke', 'jan Menki', 'jan Menko', 'jan Menku', 'jan Menla', 'jan Menle', 'jan Menli', 'jan Menlo', 'jan Menlu', 'jan Menpa', 'jan Menpe', 'jan Menpi', 'jan Menpo', 'jan Menpu', 'jan Mensa', 'jan Mense', 'jan Mensi', 'jan Menso', 'jan Mensu', 'jan Menta', 'jan Mente', 'jan Mento', 'jan Mentu', 'jan Minja', 'jan Minje', 'jan Minjo', 'jan Minju', 'jan Minka', 'jan Minke', 'jan Minki', 'jan Minko', 'jan Minku', 'jan Minla', 'jan Minle', 'jan Minli', 'jan Minlo', 'jan Minlu', 'jan Minpa', 'jan Minpe', 'jan Minpi', 'jan Minpo', 'jan Minpu', 'jan Minsa', 'jan Minse', 'jan Minsi', 'jan Minso', 'jan Minsu', 'jan Minta', 'jan Minte', 'jan Minto', 'jan Mintu', 'jan Monja', 'jan Monje', 'jan Monjo', 'jan Monju', 'jan Monka', 'jan Monke', 'jan Monki', 'jan Monko', 'jan Monku', 'jan Monla', 'jan Monle', 'jan Monli', 'jan Monlo', 'jan Monlu', 'jan Monpa', 'jan Monpe', 'jan Monpi', 'jan Monpo', 'jan Monpu', 'jan Monsa', 'jan Monse', 'jan Monsi', 'jan Monso', 'jan Monsu', 'jan Monta', 'jan Monte', 'jan Monto', 'jan Montu', 'jan Munja', 'jan Munje', 'jan Munjo', 'jan Munju', 'jan Munka', 'jan Munke', 'jan Munki', 'jan Munko', 'jan Munku', 'jan Munla', 'jan Munle', 'jan Munli', 'jan Munlo', 'jan Munlu', 'jan Munpa', 'jan Munpe', 'jan Munpi', 'jan Munpo', 'jan Munpu', 'jan Munsa', 'jan Munse', 'jan Munsi', 'jan Munso', 'jan Munsu', 'jan Munta', 'jan Munte', 'jan Munto', 'jan Muntu', 'jan Nanja', 'jan Nanje', 'jan Nanjo', 'jan Nanju', 'jan Nanka', 'jan Nanke', 'jan Nanki', 'jan Nanko', 'jan Nanku', 'jan Nanla', 'jan Nanle', 'jan Nanli', 'jan Nanlo', 'jan Nanlu', 'jan Nanpa', 'jan Nanpe', 'jan Nanpi', 'jan Nanpo', 'jan Nanpu', 'jan Nansa', 'jan Nanse', 'jan Nansi', 'jan Nanso', 'jan Nansu', 'jan Nanta', 'jan Nante', 'jan Nanto', 'jan Nantu', 'jan Nenja', 'jan Nenje', 'jan Nenjo', 'jan Nenju', 'jan Nenka', 'jan Nenke', 'jan Nenki', 'jan Nenko', 'jan Nenku', 'jan Nenla', 'jan Nenle', 'jan Nenli', 'jan Nenlo', 'jan Nenlu', 'jan Nenpa', 'jan Nenpe', 'jan Nenpi', 'jan Nenpo', 'jan Nenpu', 'jan Nensa', 'jan Nense', 'jan Nensi', 'jan Nenso', 'jan Nensu', 'jan Nenta', 'jan Nente', 'jan Nento', 'jan Nentu', 'jan Ninja', 'jan Ninje', 'jan Ninjo', 'jan Ninju', 'jan Ninka', 'jan Ninke', 'jan Ninki', 'jan Ninko', 'jan Ninku', 'jan Ninla', 'jan Ninle', 'jan Ninli', 'jan Ninlo', 'jan Ninlu', 'jan Ninpa', 'jan Ninpe', 'jan Ninpi', 'jan Ninpo', 'jan Ninpu', 'jan Ninsa', 'jan Ninse', 'jan Ninsi', 'jan Ninso', 'jan Ninsu', 'jan Ninta', 'jan Ninte', 'jan Ninto', 'jan Nintu', 'jan Nonja', 'jan Nonje', 'jan Nonjo', 'jan Nonju', 'jan Nonka', 'jan Nonke', 'jan Nonki', 'jan Nonko', 'jan Nonku', 'jan Nonla', 'jan Nonle', 'jan Nonli', 'jan Nonlo', 'jan Nonlu', 'jan Nonpa', 'jan Nonpe', 'jan Nonpi', 'jan Nonpo', 'jan Nonpu', 'jan Nonsa', 'jan Nonse', 'jan Nonsi', 'jan Nonso', 'jan Nonsu', 'jan Nonta', 'jan Nonte', 'jan Nonto', 'jan Nontu', 'jan Nunja', 'jan Nunje', 'jan Nunjo', 'jan Nunju', 'jan Nunka', 'jan Nunke', 'jan Nunki', 'jan Nunko', 'jan Nunku', 'jan Nunla', 'jan Nunle', 'jan Nunli', 'jan Nunlo', 'jan Nunlu', 'jan Nunpa', 'jan Nunpe', 'jan Nunpi', 'jan Nunpo', 'jan Nunpu', 'jan Nunsa', 'jan Nunse', 'jan Nunsi', 'jan Nunso', 'jan Nunsu', 'jan Nunta', 'jan Nunte', 'jan Nunto', 'jan Nuntu', 'jan Panja', 'jan Panje', 'jan Panjo', 'jan Panju', 'jan Panka', 'jan Panke', 'jan Panki', 'jan Panko', 'jan Panku', 'jan Panla', 'jan Panle', 'jan Panli', 'jan Panlo', 'jan Panlu', 'jan Panpa', 'jan Panpe', 'jan Panpi', 'jan Panpo', 'jan Panpu', 'jan Pansa', 'jan Panse', 'jan Pansi', 'jan Panso', 'jan Pansu', 'jan Panta', 'jan Pante', 'jan Panto', 'jan Pantu', 'jan Penja', 'jan Penje', 'jan Penjo', 'jan Penju', 'jan Penka', 'jan Penke', 'jan Penki', 'jan Penko', 'jan Penku', 'jan Penla', 'jan Penle', 'jan Penli', 'jan Penlo', 'jan Penlu', 'jan Penpa', 'jan Penpe', 'jan Penpi', 'jan Penpo', 'jan Penpu', 'jan Pensa', 'jan Pense', 'jan Pensi', 'jan Penso', 'jan Pensu', 'jan Penta', 'jan Pente', 'jan Pento', 'jan Pentu', 'jan Pinja', 'jan Pinje', 'jan Pinjo', 'jan Pinju', 'jan Pinka', 'jan Pinke', 'jan Pinki', 'jan Pinko', 'jan Pinku', 'jan Pinla', 'jan Pinle', 'jan Pinli', 'jan Pinlo', 'jan Pinlu', 'jan Pinpa', 'jan Pinpe', 'jan Pinpi', 'jan Pinpo', 'jan Pinpu', 'jan Pinsa', 'jan Pinse', 'jan Pinsi', 'jan Pinso', 'jan Pinsu', 'jan Pinta', 'jan Pinte', 'jan Pinto', 'jan Pintu', 'jan Ponja', 'jan Ponje', 'jan Ponjo', 'jan Ponju', 'jan Ponka', 'jan Ponke', 'jan Ponki', 'jan Ponko', 'jan Ponku', 'jan Ponla', 'jan Ponle', 'jan Ponli', 'jan Ponlo', 'jan Ponlu', 'jan Ponpa', 'jan Ponpe', 'jan Ponpi', 'jan Ponpo', 'jan Ponpu', 'jan Ponsa', 'jan Ponse', 'jan Ponsi', 'jan Ponso', 'jan Ponsu', 'jan Ponta', 'jan Ponte', 'jan Ponto', 'jan Pontu', 'jan Punja', 'jan Punje', 'jan Punjo', 'jan Punju', 'jan Punka', 'jan Punke', 'jan Punki', 'jan Punko', 'jan Punku', 'jan Punla', 'jan Punle', 'jan Punli', 'jan Punlo', 'jan Punlu', 'jan Punpa', 'jan Punpe', 'jan Punpi', 'jan Punpo', 'jan Punpu', 'jan Punsa', 'jan Punse', 'jan Punsi', 'jan Punso', 'jan Punsu', 'jan Punta', 'jan Punte', 'jan Punto', 'jan Puntu', 'jan Sanja', 'jan Sanje', 'jan Sanjo', 'jan Sanju', 'jan Sanka', 'jan Sanke', 'jan Sanki', 'jan Sanko', 'jan Sanku', 'jan Sanla', 'jan Sanle', 'jan Sanli', 'jan Sanlo', 'jan Sanlu', 'jan Sanpa', 'jan Sanpe', 'jan Sanpi', 'jan Sanpo', 'jan Sanpu', 'jan Sansa', 'jan Sanse', 'jan Sansi', 'jan Sanso', 'jan Sansu', 'jan Santa', 'jan Sante', 'jan Santo', 'jan Santu', 'jan Senja', 'jan Senje', 'jan Senjo', 'jan Senju', 'jan Senka', 'jan Senke', 'jan Senki', 'jan Senko', 'jan Senku', 'jan Senla', 'jan Senle', 'jan Senli', 'jan Senlo', 'jan Senlu', 'jan Senpa', 'jan Senpe', 'jan Senpi', 'jan Senpo', 'jan Senpu', 'jan Sensa', 'jan Sense', 'jan Sensi', 'jan Senso', 'jan Sensu', 'jan Senta', 'jan Sente', 'jan Sento', 'jan Sentu', 'jan Sinja', 'jan Sinje', 'jan Sinjo', 'jan Sinju', 'jan Sinka', 'jan Sinke', 'jan Sinki', 'jan Sinko', 'jan Sinku', 'jan Sinla', 'jan Sinle', 'jan Sinli', 'jan Sinlo', 'jan Sinlu', 'jan Sinpa', 'jan Sinpe', 'jan Sinpi', 'jan Sinpo', 'jan Sinpu', 'jan Sinsa', 'jan Sinse', 'jan Sinsi', 'jan Sinso', 'jan Sinsu', 'jan Sinta', 'jan Sinte', 'jan Sinto', 'jan Sintu', 'jan Sonje', 'jan Sonjo', 'jan Sonju', 'jan Sonka', 'jan Sonke', 'jan Sonki', 'jan Sonko', 'jan Sonku', 'jan Sonla', 'jan Sonle', 'jan Sonli', 'jan Sonlo', 'jan Sonlu', 'jan Sonpa', 'jan Sonpe', 'jan Sonpi', 'jan Sonpo', 'jan Sonpu', 'jan Sonsa', 'jan Sonse', 'jan Sonsi', 'jan Sonso', 'jan Sonsu', 'jan Sonta', 'jan Sonte', 'jan Sonto', 'jan Sontu', 'jan Sunja', 'jan Sunje', 'jan Sunjo', 'jan Sunju', 'jan Sunka', 'jan Sunke', 'jan Sunki', 'jan Sunko', 'jan Sunku', 'jan Sunla', 'jan Sunle', 'jan Sunli', 'jan Sunlo', 'jan Sunlu', 'jan Sunpa', 'jan Sunpe', 'jan Sunpi', 'jan Sunpo', 'jan Sunpu', 'jan Sunsa', 'jan Sunse', 'jan Sunsi', 'jan Sunso', 'jan Sunsu', 'jan Sunta', 'jan Sunte', 'jan Sunto', 'jan Suntu', 'jan Tanja', 'jan Tanje', 'jan Tanjo', 'jan Tanju', 'jan Tanka', 'jan Tanke', 'jan Tanki', 'jan Tanko', 'jan Tanku', 'jan Tanla', 'jan Tanle', 'jan Tanli', 'jan Tanlo', 'jan Tanlu', 'jan Tanpa', 'jan Tanpe', 'jan Tanpi', 'jan Tanpo', 'jan Tanpu', 'jan Tansa', 'jan Tanse', 'jan Tansi', 'jan Tanso', 'jan Tansu', 'jan Tanta', 'jan Tante', 'jan Tanto', 'jan Tantu', 'jan Tenja', 'jan Tenje', 'jan Tenjo', 'jan Tenju', 'jan Tenka', 'jan Tenke', 'jan Tenki', 'jan Tenko', 'jan Tenku', 'jan Tenla', 'jan Tenle', 'jan Tenli', 'jan Tenlo', 'jan Tenlu', 'jan Tenpa', 'jan Tenpe', 'jan Tenpi', 'jan Tenpo', 'jan Tenpu', 'jan Tensa', 'jan Tense', 'jan Tensi', 'jan Tenso', 'jan Tensu', 'jan Tenta', 'jan Tente', 'jan Tento', 'jan Tentu', 'jan Tonja', 'jan Tonje', 'jan Tonjo', 'jan Tonju', 'jan Tonka', 'jan Tonke', 'jan Tonki', 'jan Tonko', 'jan Tonku', 'jan Tonla', 'jan Tonle', 'jan Tonli', 'jan Tonlo', 'jan Tonlu', 'jan Tonpa', 'jan Tonpe', 'jan Tonpi', 'jan Tonpo', 'jan Tonpu', 'jan Tonsa', 'jan Tonse', 'jan Tonsi', 'jan Tonso', 'jan Tonsu', 'jan Tonta', 'jan Tonte', 'jan Tonto', 'jan Tontu', 'jan Tunja', 'jan Tunje', 'jan Tunjo', 'jan Tunju', 'jan Tunka', 'jan Tunke', 'jan Tunki', 'jan Tunko', 'jan Tunku', 'jan Tunla', 'jan Tunle', 'jan Tunli', 'jan Tunlo', 'jan Tunlu', 'jan Tunpa', 'jan Tunpe', 'jan Tunpi', 'jan Tunpo', 'jan Tunpu', 'jan Tunsa', 'jan Tunse', 'jan Tunsi', 'jan Tunso', 'jan Tunsu', 'jan Tunta', 'jan Tunte', 'jan Tunto', 'jan Tuntu', 'jan Wanja', 'jan Wanje', 'jan Wanjo', 'jan Wanju', 'jan Wanka', 'jan Wanke', 'jan Wanki', 'jan Wanko', 'jan Wanku', 'jan Wanla', 'jan Wanle', 'jan Wanli', 'jan Wanlo', 'jan Wanlu', 'jan Wanpa', 'jan Wanpe', 'jan Wanpi', 'jan Wanpo', 'jan Wanpu', 'jan Wansa', 'jan Wanse', 'jan Wansi', 'jan Wanso', 'jan Wansu', 'jan Wanta', 'jan Wante', 'jan Wanto', 'jan Wantu', 'jan Wenja', 'jan Wenje', 'jan Wenjo', 'jan Wenju', 'jan Wenka', 'jan Wenke', 'jan Wenki', 'jan Wenko', 'jan Wenku', 'jan Wenla', 'jan Wenle', 'jan Wenli', 'jan Wenlo', 'jan Wenlu', 'jan Wenpa', 'jan Wenpe', 'jan Wenpi', 'jan Wenpo', 'jan Wenpu', 'jan Wensa', 'jan Wense', 'jan Wensi', 'jan Wenso', 'jan Wensu', 'jan Wenta', 'jan Wente', 'jan Wento', 'jan Wentu', 'jan Winja', 'jan Winje', 'jan Winjo', 'jan Winju', 'jan Winka', 'jan Winke', 'jan Winki', 'jan Winko', 'jan Winku', 'jan Winla', 'jan Winle', 'jan Winli', 'jan Winlo', 'jan Winlu', 'jan Winpa', 'jan Winpe', 'jan Winpi', 'jan Winpo', 'jan Winpu', 'jan Winsa', 'jan Winse', 'jan Winsi', 'jan Winso', 'jan Winsu', 'jan Winta', 'jan Winte', 'jan Winto', 'jan Wintu']
def rand_name(taken_names):
    name = None
    while not name or name in taken_names:
        name = random.choice(names)
    return name


class Anonymity(commands.Cog):
    """Send messages anonymously."""

    def __init__(self, bot):
        self.bot = bot
        self.data = load_json(ANON_SAVES)

        # LOL
        allow = []
        deny = []
        conns = []
        for t in self.data["allow"]:
            allow.append(tuple(t))
        for t in self.data["deny"]:
            deny.append(tuple(t))
        for t in self.data["conns"]:
            conns.append(tuple(t))
        self.data["allow"] = allow
        self.data["deny"] = deny
        self.data["conns"] = conns

    def save(self):
        save_json(ANON_SAVES, self.data)

    @property
    def conns(self):
        return self.data["conns"]

    @property
    def names(self):
        return self.data["names"]

    @property
    def allow(self):
        return self.data["allow"]

    @property
    def deny(self):
        return self.data["deny"]

    def match_pat(self, pred, pat):
        pred1, pred2 = pred
        pat1, pat2 = pat
        return (pat1 is None or pred1 == pat1) and (pat2 is None or pred2 == pat2)

    async def ensure_channel(self, channel_or_user):
        if isinstance(channel_or_user, discord.User):
            channel = await channel_or_user.create_dm()
        else:
            channel = channel_or_user
        return channel

    def pat_ids(self, ts):
        return (ts[0].id if ts[0] else None, ts[1].id if ts[1] else None)

    def pred_objs(self, pred):
        return (self.bot.get_user(pred[0]), self.bot.get_partial_messageable(pred[1]))

    def name_for(self, user):
        return self.names[str(user.id)][0]

    def one_with_name(self, target_name):
        for user, name in self.names.items():
            if name[0] == target_name:
                return self.bot.get_user(int(user))
        return None

    def refresh_names(self):
        for l in self.names.values():
            l[1] = True
        self.save()

    def targeting(self, t):
        return [targeting for targeting, target in self.conns if target == t.id]

    def add_rule(self, rules, pat, tag):
        to_add = *pat, tag
        if tag is None:
            if to_add in rules:
                return False
        else:
            if any(this_tag == tag for _, _, this_tag in rules):
                return False
        rules.append(to_add)
        return True

    def remove_rule(self, rules, pat, tag):
        if tag is None:
            try:
                rules.remove((*pat, tag))
            except ValueError:
                return False
            else:
                return True
        else:
            for i, (_, _, this_tag) in enumerate(rules):
                if this_tag == tag:
                    rules.pop(i)
                    return True
            return False

    def disable(self, pat, tag=None):
        l = [self.end_session(x) for x in self.connections(pat)]
        pat = self.pat_ids(pat)
        self.remove_rule(self.allow, pat, tag)
        if self.add_rule(self.deny, pat, tag):
            self.save()  # it looks like this save is in the wrong place but it's actually fine
            return l
        else:
            return None

    def enable(self, pat, tag=None):
        pat = self.pat_ids(pat)
        self.remove_rule(self.deny, pat, tag)
        r = self.add_rule(self.allow, pat, tag)
        self.save()
        return not r

    def start_session(self, targeting, target):
        k = (targeting.id, target.id)
        if not any(self.match_pat(k, x[:2]) for x in self.allow) or any(self.match_pat(k, x[:2]) for x in self.deny):
            return None
        new = (targeting.id, target.id)
        if new in self.conns:
            return (None, None)
        if self.names.get(str(targeting.id), (None, True))[1]:
            self.names[str(targeting.id)] = [rand_name(self.names.values()), False]
        old = self.end_session((targeting, None))
        self.conns.append(new)
        self.save()
        return (old, target)

    def end_session(self, pat):
        pat = self.pat_ids(pat)
        for i, pred in enumerate(self.conns):
            if self.match_pat(pred, pat):
                self.conns.pop(i)
                r = self.pred_objs(pred)
                self.save()
                return r
        return None

    def connections(self, pat):
        pat = self.pat_ids(pat)
        l = []
        for pred in self.conns:
            if self.match_pat(pred, pat):
                objs = self.pred_objs(pred)
                if objs[0]:
                    l.append(objs)
        return l

    async def take_user_arg(self, ctx, name, context=None):
        n = self.one_with_name(name)
        tag = name
        dn = name
        if not n:
            n = await commands.UserConverter().convert(ctx, name)
            if n.bot:
                await ctx.send("That's a bot.")
                # muahaha
                raise commands.CommandNotFound()
            tag = n.id
            dn = n.display_name
        return n, [*context, tag], dn

    @commands.dm_only()
    @commands.group(invoke_without_command=True)
    async def anon(self, ctx, target: Union[discord.User, discord.TextChannel, discord.Thread]):
        """Use in DMs with Esobot to anonymously message a user or channel."""
        if isinstance(target, discord.User) and target.bot:
            return await ctx.send("That's a bot, silly!")
        if not (isinstance(target, discord.User) or (member := target.guild.get_member(ctx.author.id)) and target.permissions_for(member).send_messages):
            return await ctx.send("You can't speak in that channel.")

        if isinstance(target, discord.User) and self.connections((None, await self.ensure_channel(ctx.author))):
            return await ctx.send("You can't talk to another user anonymously while you're already being talked to by someone else.")
        if isinstance(target, discord.User) and any([isinstance(self.bot.get_channel(targeted.id), (discord.DMChannel, type(None))) for _, targeted in self.connections((target, None))]):
            return await ctx.send("You can't talk to this user; they're already talking to someone else anonymously.")

        o = self.start_session(ctx.author, await self.ensure_channel(target))
        if not o:
            if isinstance(target, discord.User):
                p = get_pronouns(target)
                return await ctx.send(f"You are blocked or that person is not accepting anonymous connections. Consider contacting {p.obj} to get {p.obj} to opt into anonymous messaging. Don't blow your cover, though!")
            else:
                return await ctx.send("You are blocked or anonymous connections are not enabled for that channel. Consider contacting the server admins to get them to enable it. Don't blow your cover, though!")

        name = self.name_for(ctx.author)
        old, new = o
        if not new:
            return await ctx.send("But nothing changed.")
        if old:
            await old[1].send(f"{self.name_for(old[0])} left.")

        if isinstance(target, discord.User):
            p = get_pronouns(target)
            where = f"to {p.obj}"
            prep = "with"
            await new.send(f"You are being messaged anonymously by '{name}'.")
        else:
            where = "there"
            prep = "in"
            await new.send(f"An anonymous user ({name}) joined the channel.")

        await ctx.send(f"Started a session {prep} {target.mention}. All the messages you send (except commands) after this point will be sent {where}.\n"
                       f"You are *{name}*. Do `!anon leave` to stop bridging.\n"
                       "Note: Automatic normalization of orthography is applied to each message. "
                       "Avoid this for a single message by prefixing it with `\\`.\n"
                       "**NB**: Full anonymity is not guaranteed. Your identity can be accessed by the developer of the bot.\n"
                       "**NB**: If you inadvertently reveal your own identity, contact LyricLy so she can refresh the names. Post-refresh, you'll get a new name when you next use `anon`.")

    @commands.dm_only()
    @anon.command(aliases=["stop"])
    async def leave(self, ctx):
        """Leave a channel which you are anonymously messaging."""
        if p := self.end_session((ctx.author, None)):
            await p[1].send(f"{self.name_for(p[0])} left.")
            await ctx.send("Left.")
        else:
            await ctx.send("?")

    @commands.dm_only()
    @anon.command(aliases=["hide", "cower", "opt-out", "out"])
    async def optout(self, ctx):
        """Opt out of being anonymously messaged in your DMs. Undoes `optin`."""
        l = self.disable((None, await self.ensure_channel(ctx.author)))
        if l is None:
            return await ctx.send("?")
        for u in l:
            await u[0].send("Your anonymous session was forcibly closed by the recipient opting out.")
        names = [self.name_for(x[0]) for x in l]
        match names:
            case []:
                report = ""
            case [x]:
                report = f" and disconnected {x}"
            case [x, y]:
                report = f" and disconnected {x} and {y}"
            case [*xs, y]:
                report = f" and disconnected {', '.join(xs)}, and {y}"
        await ctx.send(f"Alright. Stopped incoming connections{report}.")

    @commands.dm_only()
    @anon.command(aliases=["unhide", "return", "opt-in", "in"])
    async def optin(self, ctx):
        """Opt in to receiving messages anonymously in your DMs."""
        if self.enable((None, await self.ensure_channel(ctx.author))):
            return await ctx.send("?")
        await ctx.send("Enabled. Good luck.")

    @commands.dm_only()
    @anon.command()
    async def block(self, ctx, *, name):
        """Block a particular anonymous user to stop them DMing you."""
        
        n, tag, dn = await self.take_user_arg(ctx, name, ("block", ctx.author.id))

        l = self.disable((n, await self.ensure_channel(ctx.author)), tag)
        if l is None:
            return await ctx.send("You already have them blocked.")
        for u in l:
            await u[0].send("Your anonymous session was forcibly closed by the recipient blocking you.")

        report = " and disconnected them"*(bool(l) and isinstance(n, str))
        await ctx.send(f"Alright. Blocked {dn}{report}.")

    @commands.dm_only()
    @anon.command()
    async def unblock(self, ctx, *, name):
        """Unblock a user. Undoes `block`."""
        n, tag, dn = await self.take_user_arg(ctx, name, ("block", ctx.author.id))
        if self.enable((n, await self.ensure_channel(ctx.author)), tag):
            return await ctx.send("They weren't blocked.")
        await ctx.send(f"Okay, {dn} can message you anonymously now.")

    @commands.has_permissions(manage_channels=True)
    @anon.command(name="enable")
    async def _enable(self, ctx, *, channel: discord.TextChannel = None):
        """Let a channel be messaged anonymously."""
        channel = channel or ctx.channel
        if self.enable((None, channel)):
            return await ctx.send("That was already enabled, but I double-enabled it to make sure.\n(Narrator: It did not.)")
        await ctx.send("Enjoy the spam or whatever.")

    @commands.has_permissions(manage_channels=True)
    @anon.command(name="disable")
    async def _disable(self, ctx, *, channel: discord.TextChannel = None):
        """The inverse of `enable`."""
        channel = channel or ctx.channel
        l = self.disable((None, channel))
        if l is None:
            return await ctx.send("Wasn't enabled in the first place, but okay.")
        for u in l:
            await u[0].send("Your anonymous session was closed forcibly because the channel's access was disabled.")
        await ctx.send("No more spam.")

    @commands.has_permissions(kick_members=True)  # I'd like this to be timeouts but dpy of course doesn't have the perm
    @anon.command()
    async def unmute(self, ctx, channel: Optional[discord.TextChannel] = None, *, name):
        """Unmute a user, reversing `mute`."""
        channel = channel or ctx.channel
        n, tag, _ = await self.take_user_arg(ctx, name, ("mute", channel.id))
        if self.enable((n, channel), tag):
            return await ctx.send("They weren't muted.")
        await ctx.send("They're back.")

    @commands.has_permissions(kick_members=True)
    @anon.command()
    async def mute(self, ctx, channel: Optional[discord.TextChannel] = None, *, name):
        """Mute a user in a single channel, stopping them from being able to use anonymous messaging there."""
        channel = channel or ctx.channel
        n, tag, _ = await self.take_user_arg(ctx, name, ("mute", channel.id))
        l = self.disable((n, channel), tag)
        if l is not None:
            for u in l:
                await u[0].send("Your anonymous session was closed forcibly because you were muted.")
        await ctx.send("They're gone.")

    @anon.command(aliases=["list"])
    async def who(self, ctx):
        """List the anonymous users connected to the current channel."""
        names = [self.name_for(x[0]) for x in self.connections((None, ctx.channel))]
        if not names:
            await ctx.send("There's nobody here.")
        else:
            await ctx.send(f"{len(names)} user{'s'*(len(names)>1)} connected ({', '.join(names)})")

    @commands.is_owner()
    @anon.command()
    async def halt(self, ctx, *, name):
        n, _, _ = await self.take_user_arg(ctx, name)
        l = self.disable((n, None))
        if l is None:
            return await ctx.send("Not sure how you forgot that you already did that, but yeah, they were already super banned.")
        for u in l:
            await u[0].send("Your anonymous session was closed forcibly because you were banned from the entire bot. Well done.")
        await ctx.send("They're gone for good. Unless you let them come back.")

    @commands.is_owner()
    @anon.command()
    async def unhalt(self, ctx, *, name):
        n, _, _ = await self.take_user_arg(ctx, name)
        if self.enable((n, None)):
            return await ctx.send("No, they were alright, actually. They weren't banned.")
        await ctx.send("'Tis the season for forgiveness. Unless it isn't Christmas time any more. It roughly was at the time of writing. Anyway, they're unbanned.")

    @commands.is_owner()
    @anon.command(aliases=["uncover", "reveal", "deanon", "de"])
    async def see(self, ctx, *, target_name):
        if not (u := self.one_with_name(target_name)):
            return await ctx.send("Nobody here is called that.")
        await ctx.send(f"That's {u}.")

    @commands.is_owner()
    @anon.command()
    async def refresh(self, ctx):
        self.refresh_names()
        await ctx.send("Done.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.guild and not message.content.startswith("!") and (t := self.connections((message.author, None))):
            target = t[0][1]
            content = message.content
            if content.startswith("\\"):
                content = content[1:]
            else:
                content = content.lower().replace(",", "").replace("'", "").replace(".", "").replace("?", "")
            await target.send(f"<{self.name_for(message.author)}> {content}", embeds=message.embeds, files=[await f.to_file() for f in message.attachments])

        for connection in self.connections((None, message.channel)):
            # don't relay our own relays
            if message.author == self.bot.user and message.content.startswith(f"<{self.name_for(connection[0])}>"):
                continue
            # don't relay ourselves in DMs
            if not message.guild and (message.author == self.bot.user or message.content.startswith("!")):
                continue
            try:
                await connection[0].send(f"<{message.author.display_name}> {message.content}", embeds=message.embeds, files=[await f.to_file() for f in message.attachments])
            except discord.Forbidden:
                pass

async def setup(bot):
    await bot.add_cog(Anonymity(bot))
