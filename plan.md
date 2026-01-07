azalt(...)
Calculate horizontal coordinates (azimuth and altitude) of a planet or a star from either ecliptical or equatorial coordinates.
 
:Args: float tjdut, int flag, seq geopos, float atpress, float attemp, seq xin
 
 - tjdut: input time, Julian day number, Universal Time
 - flag: either ECL2HOR (from ecliptical coord) or EQU2HOR (equatorial)
 - geopos: a sequence with:
    - 0: geographic longitude, in degrees (eastern positive)
    - 1: geographic latitude, in degrees (northern positive)
    - 2: geographic altitude, in meters above sea level
 - atpress: atmospheric pressure in mbar (hPa)
 - attemp: atmospheric temperature in degrees Celsius
 - xin: a sequence with:
    - ECL2HOR: ecl. longitude, ecl. latitude, distance
    - EQU2HOR: right ascension, declination, distance
 
:Return: float azimuth, true_altitude, apparent_altitude
 
 - azimuth: position degree, measured from south point to west
 - true_altitude: true altitude above horizon in degrees
 - apparent_altitude: apparent (refracted) altitude above horizon in   degrees
 
The apparent altitude of a body depends on the atmospheric pressure and temperature. If only the true altitude is required, these parameters can be neglected.
 
If ``atpress`` is given the value 0, the function estimates the pressure from the geographical altitude given in ``xin[3]`` and ``attemp``. If ``xin[3]`` is 0, ``atpress`` will be estimated for sea level.
azalt_rev(...)
Calculate either ecliptical or equatorial coordinates from azimuth and true altitude.
 
:Args: float tjdut, int flag, seq geopos, double azimuth, double true_altitude
 
 - tjdut: input time, Julian day number, Universal Time
 - flag: either HOR2ECL (to ecliptical coord) or HOR2EQU (to equatorial)
 - geopos: a sequence with:
    - 0: geographic longitude, in degrees (eastern positive)
    - 1: geographic latitude, in degrees (northern positive)
    - 2: geographic altitude, in meters above sea level)
 - azimuth: position degree, measured from south point to west
 - true_altitude: true altitude above horizon in degrees
 
:Return: float x1, x2
 
 - x1, x2: ecliptical or equatorial coordinates, depending on flag
 
This function is not precisely the reverse of ``azalt()``. It computes either ecliptical or equatorial coordinates from azimuth and true altitude. If only an apparent altitude is given, the true altitude has to be computed first with the function ``refrac()``.
calc(...)
Calculate planetary positions (ET).
 
:Args: float tjdet, int planet, int flags=FLG_SWIEPH|FLG_SPEED
 
 - tjdet: Julian day, Ephemeris Time, where tjdet == tjdut + deltat(tjdut)
 - planet: body number
 - flags: bit flags indicating what kind of computation is wanted
 
:Return: (xx), int retflags
 
 - xx: tuple of 6 float for results
 - retflags: bit flags indicating what kind of computation was done
 
This function can raise swisseph.Error in case of fatal error.
calc_pctr(...)
Calculate planetocentric positions of planets (ET).
 
:Args: float tjd, int planet, int center, int flags=FLG_SWIEPH|FLG_SPEED
 
 - tjdet: julian day in ET (TT)
 - planet: body number of target object
 - center: body number of center object
 - flags: bit flags indicating what kind of computation is wanted
 
:Return: (xx), int retflags
 
 - xx: tuple of 6 float for results
 - retflags: bit flags indicating what kind of computation was done
 
This function can raise swisseph.Error in case of fatal error.
calc_ut(...)
Calculate planetary positions (UT).
 
:Args: float tjdut, int planet, int flags=FLG_SWIEPH|FLG_SPEED
 
 - tjdut: julian day number, universal time
 - planet: body number
 - flags: bit flags indicating what kind of computation is wanted
 
:Return: (xx), int retflags
 
 - xx: tuple of 6 float for results
 - retflags: bit flags indicating what kind of computation was done
 
This function can raise swisseph.Error in case of fatal error.
close(...)
Close Swiss Ephemeris.
 
:Args: --
:Return: None
 
At the end of your computations you can release all resources (open files and allocated memory) used by the swisseph module.
 
After ``close()``, no swisseph functions should be used unless you call ``set_ephe_path()`` again and, if required, ``set_jpl_file()``.
cotrans(...)
Coordinate transformation from ecliptic to equator or vice-versa.
 
:Args: seq coord, float eps
 
 - coord: tuple of 3 float for coordinates:
    - 0: longitude
    - 1: latitude
    - 2: distance (unchanged, can be set to 1)
 - eps: obliquity of ecliptic, in degrees
 
:Return: float retlon, retlat, retdist
 
 - retlon: converted longitude
 - retlat: converted latitude
 - retdist: converted distance
 
For equatorial to ecliptical, obliquity must be positive. From ecliptical to equatorial, obliquity must be negative. Longitude, latitude and obliquity are in positive degrees.
cotrans_sp(...)
Coordinate transformation of position and speed, from ecliptic to equator or vice-versa.
 
:Args: seq coord, float eps
 
 - coord: tuple of 6 float for coordinates:
    - 0: longitude
    - 1: latitude
    - 2: distance
    - 3: longitude speed
    - 4: latitude speed
    - 5: distance speed
 - eps: obliquity of ecliptic, in degrees
 
:Return: float retlon, retlat, retdist, retlonsp, retlatsp, retdistsp
 
 - retlon, retlonsp: converted longitude and its speed
 - retlat, retlatsp: converted latitude and its speed
 - retdist, retdistsp: converted distance and its speed
 
For equatorial to ecliptical, obliquity must be positive. From ecliptical to equatorial, obliquity must be negative. Longitude, latitude, their speeds and obliquity are in positive degrees.
cs2degstr(...)
Get degrees string from centiseconds.
 
:Args: int cs
:Return: str retstr
cs2lonlatstr(...)
Get longitude or latitude string from centiseconds.
 
:Args: int cs, bytes plus, bytes minus
:Return: str retstr
 
This function raises TypeError if plus or minus parameter length is not exactly 1 byte.
cs2timestr(...)
Get time string from centiseconds.
 
:Args: int cs, bytes sep, bool suppresszero=False
:Return: str retstr
 
This function raises TypeError if sep parameter length is not exactly 1 byte.
csnorm(...)
Normalization of any centisecond number to the range [0;360].
 
:Args: int cs
:Return: int retcs
csroundsec(...)
Round centiseconds, but at 29.5959 always down.
 
:Args: int cs
:Return: int retcs
d2l(...)
Double to integer with rounding, no overflow check.
 
:Args: float d
:Return: int i
date_conversion(...)
Calculate Julian day number with check wether input date is correct.
 
:Args: int year, int month, int day, float hour=12.0, bytes cal=b'g'
 
 - year, month, day: input date
 - hour: input time, decimal with fraction
 - cal: calendar type, gregorian (b'g') or julian (b'j')
 
:Return: bool isvalid, float jd, (dt)
 
 - isvalid: True if the input date and time are legal
 - jd: returned Julian day number
 - dt: a tuple for, if input was not valid, corrected year, month, day, hour;
   if input was valid, contains input date and time
 
This function raises TypeError if cal length is not exactly 1 byte.
It raises ValueError if cal is not b'g' or b'j'.
day_of_week(...)
Calculate day of week number [0;6] from Julian day number (monday is 0).
 
:Args: float jd
:Return: int dow
deg_midp(...)
Calculate midpoint (in degrees).
 
:Args: float x1, float x2
:Return: float midp
degnorm(...)
Normalization of any degree number to the range [0;360[.
 
:Args: float x
:Return: float xnorm
deltat(...)
Calculate value of delta T from Julian day number.
 
:Args: float tjdut
 
- tjdut: input time, Julian day number, Universal Time
 
:Return: float deltat
 
 - deltat: returned delta T value
 
Reminder::
 
   tjdet == tjdut + deltat(tjdut)
 
This function is safe only if your application consistently uses the same ephemeris flags, if your application consistently uses the same ephemeris files, if you first call ``set_ephe_path()`` (with flag ``FLG_SWIEPH``) or ``set_jpl_file()`` (with flag ``FLG_JPLEPH``).
 
Also, it is safe if you first call ``set_tid_acc()`` with the tidal acceleration you want. However, do not use that function unless you know what you are doing.
 
For best control of the values returned, use function ``deltat_ex()`` instead.
 
The calculation of ephemerides in UT depends on Delta T, which depends on the ephemeris-inherent value of the tidal acceleration of the Moon. In default mode, the function ``deltat()`` automatically tries to find the required values.
 
Two warnings must be made, though:
 
 - It is not recommended to use a mix of old and new ephemeris files, because the old files were based on JPL Ephemeris DE406, whereas the new ones are based on DE431, and both ephemerides have a different inherent tidal acceleration of the Moon. A mixture of old and new ephemeris files may lead to inconsistent ephemeris output. Using old asteroid files ``se99999.se1`` together with new ones, can be tolerated, though.
 - The function ``deltat()`` uses a default value of tidal acceleration (that of DE431). However, after calling some older ephemeris, like Moshier ephemeris, DE200, or DE406, ``deltat()`` might provide slightly different values.
 
In case of troubles related to these two points, it is recommended to either use function ``deltat_ex()``, or control the value of the tidal acceleration using the functions ``set_tid_acc()`` and ``get_tid_acc()``.
deltat_ex(...)
Calculate value of Delta T from Julian day number (extended).
 
:Args: float tjdut, int flag
 
 - tjdut: input time, Julian day number, Universal Time
 - flag: ephemeris flag, ``FLG_SWIEPH`` ``FLG_JPLEPH`` ``FLG_MOSEPH``
 
:Return: float deltat
 
 - deltat: returned delta T value
 
Calling this function without a previous call of ``set_ephe_path()`` or  ``set_jpl_file()`` will raise swisseph.Error.
 
The calculation of ephemerides in UT depends on the ephemeris-inherent value of the tidal acceleration of the Moon. The function ``deltat_ex()`` can provide ephemeris-dependent values of Delta T and is therefore better than the old function ``deltat()``, which has to make un uncertain guess of what ephemeris is being used. One warning must be made, though:
 
It is not recommended to use a mix of old and new ephemeris files, because the old files were based on JPL Ephemeris DE406, whereas the new ones are based on DE431, and both ephemerides have a different inherent tidal acceleration of the Moon. A mixture of old and new ephemeris files may lead to inconsistent ephemeris output. Using old asteroid files ``se99999.se1`` together with new ones, can be tolerated, though.
difcs2n(...)
Calculate distance in centisecs p1 - p2 normalized to [-180;180].
 
:Args: int p1, int p2
:Return: int dist
difcsn(...)
Calculate distance in centisecs p1 - p2.
 
:Args: int p1, int p2
:Return: int dist
difdeg2n(...)
Calculate distance in degrees p1 - p2 normalized to [-180;180].
 
:Args: float p1, float p2
:Return: float dist
difdegn(...)
Calculate distance in degrees p1 - p2.
 
:Args: float p1, float p2
:Return: float dist
difrad2n(...)
Calculate distance in radians p1 - p2 normalized to [-180;180].
 
:Args: float p1, float p2
:Return: float dist
fixstar(...)
Calculate fixed star positions (ET).
 
:Args: str star, float tjdet, int flags=FLG_SWIEPH
 
 - star: name of fixed star to search for
 - tjdet: input time, Julian day number,  Ephemeris Time
 - flags: bit flags indicating what kind of computation is wanted
 
:Return: (xx), str stnam, int retflags
 
 - xx: tuple of 6 float for results
 - stnam: returned star name
 - retflags: bit flags indicating what kind of computation was done
 
This function raises swisseph.Error in case of fatal error.
fixstar2(...)
Calculate fixed star positions (faster version) (ET).
 
:Args: str star, float tjdet, int flags=FLG_SWIEPH
 
 - star: name of fixed star to search for
 - tjdet: input time, Julian day number, Ephemeris Time
 - flags: bit flags indicating what kind of computation is wanted
 
:Return: (xx), str stnam, int retflags
 
 - xx: tuple of 6 float for results
 - stnam: returned star name
 - retflags: bit flags indicating what kind of computation was done
 
This function raises swisseph.Error in case of fatal error.
fixstar2_mag(...)
Get fixed star magnitude (faster version).
 
:Args: str star
 
 - star: name of fixed star
 
:Return: float mag, str stnam
 
 - mag: returned magnitude
 - stnam: returned star name
 
This function raises swisseph.Error in case of fatal error.
fixstar2_ut(...)
Calculate fixed star positions (faster version) (UT).
 
:Args: str star, float tjdut, int flags=FLG_SWIEPH
 
 - star: name of fixed star to search for
 - tjdut: inputtime, Julian day nnumber, Universal Time
 - flags: bit flags indicating what kind of computation is wanted
 
:Return: (xx), str stnam, int retflags
 
 - xx: tuple of 6 float for results
 - stnam: returned star name
 - retflags: bit flags indicating what kind of computation was done
 
This function raises swisseph.Error in case of fatal error.
fixstar_mag(...)
Get fixed star magnitude.
 
:Args: str star
 
 - star: name of fixed star
 
:Return: float mag, str stnam
 
 - mag: returned magnitude
 - stnam: returned star name
 
This function raises swisseph.Error in case of fatal error.
fixstar_ut(...)
Calculate fixed star positions (UT).
 
:Args: str star, float tjdut, int flags=FLG_SWIEPH
 
 - star: name of fixed star to search for
 - tjdut: input time, Julian day number,  Universal Time
 - flags: bit flags indicating what kind of computation is wanted
 
:Return: (xx), str stnam, int retflags
 
 - xx: tuple of 6 float for results
 - stnam: returned star name
 - retflags: bit flags indicating what kind of computation was done
 
This function raises swisseph.Error in case of fatal error.
gauquelin_sector(...)
Calculate Gauquelin sector position of a body (UT).
 
:Args: float tjdut, int or str body, int method, seq geopos, float atpress=0, float attemp=0, int flags=FLG_SWIEPH|FLG_TOPOCTR
 
 - tjdut: input time, Julian day number, Universal Time
 - body: planet number (int) or fixed star name (str)
 - method: number indicating which computation method is wanted:
    - 0 with latitude
    - 1 without latitude
    - 2 from rising and setting times of the disc center of planet
    - 3 from rising and setting times of disc center, incl. refraction
    - 4 from rising and setting times of the disk edge of planet
    - 5 from rising and setting times of disk edge, incl. refraction
 - geopos: a sequence containing:
    - 0: geographic longitude, in degrees (eastern positive)
    - 1: geographic latitude, in degrees (northern positive)
    - 2: geographic altitude, in meters above sea level
 - atpress: atmospheric pressure (if 0, the default 1013.25 mbar is used)
 - attemp: atmospheric temperature in degrees Celsius
 - flags: bit flags for ephemeris and FLG_TOPOCTR, etc
 
:Return: float sector
 
 - sector: [1;37[. Gauquelin sectors are numbered in clockwise direction.
 
This function raises swisseph.Error in case of fatal error.
get_ayanamsa(...)
Calculate ayanamsa (ET).
 
:Args: float tjdet
 
 - tjdet: input time, Julian day number, Ephemeris Time
 
:Return: float aya
 
 - aya: ayanamsa value, without nutation
get_ayanamsa_ex(...)
Calculate ayanamsa, extended version (ET).
 
:Args: float tjdet, int flags
 
 - tjdet: input time, Julian day number, Ephemeris Time
 - flags: ephemeris flag, etc
 
:Return: int retflags, float aya
 
 - retflags: returned bit flags
 - aya: ayanamsa value
 
This function raises swisseph.Error in case of fatal error.
get_ayanamsa_ex_ut(...)
Calculate ayanamsa, extended version (UT).
 
:Args: float tjdut, int flags
 
 - tjdut: input time, Julian day number, Universal Time
 - flags: ephemeris flag, etc
 
:Return: int retflags, float aya
 
 - retflags: returned bit flags
 - aya: ayanamsa value
 
This function raises swisseph.Error in case of fatal error.
get_ayanamsa_name(...)
Get ayanamsa name from sidereal mode constant.
 
:Args: int sidmode
:Return: str name
 
If sidmode is not found (incorrect), returned string is empty.
get_ayanamsa_ut(...)
Calculate ayanamsa (UT).
 
:Args: float tjdut
 
 - tjdut: input time, Julian day number, Universal Time
 
:Return: float aya
 
 - aya: ayanamsa value, without nutation
get_current_file_data(...)
Find start and end date of an se1 ephemeris file after a function call.
 
:Args: int fno
 
 - fno: an integer indicating what type of file is searched:
    - 0: planet file sepl_xxx, used for Sun etc, or jpl file
    - 1: moon file semo_xxx
    - 2: main asteroid file seas_xxx, if such an object was computed
    - 3: other asteroid or planetary moon file, if such object was computed
    - 4: star file
 
:Return: str path, float start, float end, int denum
 
 - path: full file path, or empty string if no data
 - start: start date of file
 - end: end date of file
 - denum: jpl ephemeris number 406 or 431 from which file was derived
 
This can be used to find out the start and end date of an ``se1`` ephemeris file after a call of ``calc()``.
 
The function returns data from internal file structures ``sweph.fidat`` used in the last call to ``calc()`` or ``fixstar()``. Data returned are (currently) 0 with JPL files and fixed star files. Thus, the function is only useful for ephemerides of planets or asteroids that are based on ``se1`` files.
get_library_path(...)
Find the path of the executable or swisseph library (dll) actually in use.
 
:Args: --
:Return: str path
 
.. note::
 
    This function may fail on Windows, and only find the executable path, not the dll.
get_orbital_elements(...)
Calculate osculating elements (Kepler elements) and orbital periods.
 
:Args: float tjdet, int planet, int flags
 
 - tjdet: input time, Julian day number, Ephemeris Time (TT)
 - planet: identifier of planet or object
 - flags: bit flags indicating what computation is wanted:
    - ephemeris flag: FLG_JPLEPH, FLG_SWIEPH, FLG_MOSEPH, etc
    - center:
       - Sun: FLG_HELCTR (assumed as default) or
       - SS Barycentre: FLG_BARYCTR (rel. to solar system barycentre)
         Only possible for planets beyond Jupiter.
         For elements of the Moon, the calculation is geocentric.
    - sum all masses inside the orbit to be computed (method of
      Astronomical Almanac): FLG_ORBEL_AA
    - reference ecliptic: FLG_J2000
 
:Return: (elements)
 
 - elements: a tuple of 50 float, of which:
    - 0: semimajor axis (a)
    - 1: eccentricity (e)
    - 2: inclination (in)
    - 3: longitude of ascending node (upper-case omega OM)
    - 4: argument of periapsis (lower-case omega om)
    - 5: longitude of periapsis (peri)
    - 6: mean anomaly at epoch (M0)
    - 7: true anomaly at epoch (N0)
    - 8: eccentric anomaly at epoch (E0)
    - 9: mean longitude at epoch (LM)
    - 10: sidereal orbital period in tropical years
    - 11: mean daily motion
    - 12: tropical period in years
    - 13: synodic period in days, negative for inner planets or Moon
    - 14: time of perihelion passage
    - 15: perihelion distance
    - 16: aphelion distance
 
This function raises swisseph.Error in case of fatal error.
get_planet_name(...)
Get a planet or asteroid name.
 
:Args: int planet
 
 - planet: identifier of planet or object
 
:Return: str name
 
 - name: name found or empty string
 
If an asteroid name is wanted, the function does the following:
 
The name is first looked for in the asteroid ephemeris file.
 
Because many asteroids, especially the ones with high catalogue numbers, have no names yet (or have only a preliminary designation like 1968 HB), and because the Minor Planet Center of the IAU add new names quite often, it happens that there is no name in the asteroid file although the asteroid has already been given a name.
 
For this, we have the file ``seasnam.txt``, a file that contains a list of all named asteroid and is usually more up to date. If ``calc()`` finds a preliminary designation, it looks for a name in this file.
 
The file ``seasnam.txt`` can be updated by the user. To do this, download the names list from the Minor Planet Center https://www.minorplanetcenter.net/iau/lists/MPNames.html, rename it as ``seasnam.txt`` and move it into your ephemeris directory.
 
The file ``seasnam.txt`` need not be ordered in any way. There must be one asteroid per line, first its catalogue number, then its name. The asteroid number may or may not be in brackets.
get_tid_acc(...)
Get current value of the tidal acceleration.
 
:Args: --
:Return: float tidacc
heliacal_pheno_ut(...)
Provides data that are relevant for the calculation of heliacal risings and settings.
 
:Args: float tjdut, seq geopos, seq atmo, seq observer, str objname, int eventtype, int flags
 
 - tjdut: input time, Julian day number, Universal Time
 - geopos: a sequence with:
    - 0: geographic longitude (eastern positive)
    - 1: geographic latitude (northern positive)
    - 2: altitude above sea level, in meters
 - atmo: a sequence with:
    - 0: atmospheric pressure in mbar (hPa)
    - 1: atmospheric temperature in degrees Celsius
    - 2: relative humidity in %
    - 3: if >= 1, Meteorological Range (km).
      Between 1 and 0, total atmospheric coefficient (ktot).
      If = 0, the other atmospheric parameters determine the total
      atmospheric coefficient (ktot)
 - observer: a sequence with:
    - 0: age of observer in years (default = 36)
    - 1: snellen ratio of observers eyes (default = 1 = normal)
    - The following parameters are only relevant if HELFLAG_OPTICAL_PARAMS
      is set:
    - 2: (0) = monocular, (1) = binocular (boolean)
    - 3: telescope magnification, (0) = default to naked eye (binocular),
      (1) = naked eye
    - 4: optical aperture (telescope diameter) in mm
    - 5: optical transmission
 - objname: name of planet or fixed star
 - eventtype: either:
    - HELIACAL_RISING: morning first, for all visible planets and stars
    - HELIACAL_SETTING: evening last, for all visible planets and stars
    - EVENING_FIRST: evening first, for Mercury, Venus, Moon
    - MORNING_LAST: morning last, for Mercury, Venus, Moon
 - flags: bit flags for ephemeris, and also:
    - HELFLAG_OPTICAL_PARAMS: for optical instruments
    - HELFLAG_NO_DETAILS: provide date, without details
    - HELFLAG_VISLIM_DARK: behave as if Sun is at nadir
    - HELFLAG_VISLIM_NOMOON: behave as if Moon is at nadir, i.e. the Moon as
      a factor disturbing the observation is excluded, useful if one is not
      interested in the heliacal date of that particular year, but in the
      heliacal date of that epoch
 
:Return: (dret)
 
 - dret: tuple of 50 float, of which:
    - 0: AltO [deg] topocentric altitude of object (unrefracted)
    - 1: AppAltO [deg] apparent altitude of object (refracted)
    - 2: GeoAltO [deg] geocentric altitude of object
    - 3: AziO [deg] azimuth of object
    - 4: AltS [deg] topocentric altitude of Sun
    - 5: AziS [deg] azimuth of Sun
    - 6: TAVact [deg] actual topocentric arcus visionis
    - 7: ARCVact [deg] actual (geocentric) arcus visionis
    - 8: DAZact [deg] actual difference between object's and sun's azimuth
    - 9: ARCLact [deg] actual longitude difference between object and sun
    - 10: kact [-] extinction coefficient
    - 11: minTAV [deg] smallest topocentric arcus visionis
    - 12: TfistVR [JDN] first time object is visible, according to VR
    - 13: TbVR [JDN] optimum time the object is visible, according to VR
    - 14: TlastVR [JDN] last time object is visible, according to VR
    - 15: TbYallop [JDN] best time the object is visible, according to Yallop
    - 16: WMoon [deg] crescent width of Moon
    - 17: qYal [-] q-test value of Yallop
    - 18: qCrit [-] q-test criterion of Yallop
    - 19: ParO [deg] parallax of object
    - 20: Magn [-] magnitude of object
    - 21: RiseO [JDN] rise/set time of object
    - 22: RiseS [JDN] rise/set time of Sun
    - 23: Lag [JDN] rise/set time of object minus rise/set time of Sun
    - 24: TvisVR [JDN] visibility duration
    - 25: LMoon [deg] crescent length of Moon
    - 26: CVAact [deg]
    - 27: Illum [%] new
    - 28: CVAact [deg] new
    - 29: MSk [-]
 
This function raises swisseph.Error in case of fatal error.
heliacal_ut(...)
Find the Julian day of the next heliacal phenomenon.
 
:Args: float tjdut, seq geopos, seq atmo, seq observer, str objname, int eventtype, int flags
 
 - tjdut: input time, Julian day number, Universal Time
 - geopos: a sequence with:
    - 0: geographic longitude (eastern positive)
    - 1: geographic latitude (northern positive)
    - 2: altitude above sea level, in meters
 - atmo: a sequence with:
    - 0: atmospheric pressure in mbar (hPa)
    - 1: atmospheric temperature in degrees Celsius
    - 2: relative humidity in %
    - 3: if >= 1, Meteorological Range (km).
      Between 1 and 0, total atmospheric coefficient (ktot).
      If = 0, the other atmospheric parameters determine the total
      atmospheric coefficient (ktot)
 - observer: a sequence with:
    - 0: age of observer in years (default = 36)
    - 1: snellen ratio of observers eyes (default = 1 = normal)
    - The following parameters are only relevant if HELFLAG_OPTICAL_PARAMS
      is set:
    - 2: (0) = monocular, (1) = binocular (boolean)
    - 3: telescope magnification, (0) = default to naked eye (binocular),
      (1) = naked eye
    - 4: optical aperture (telescope diameter) in mm
    - 5: optical transmission
 - objname: name of planet or fixed star
 - eventtype: either:
    - HELIACAL_RISING: morning first, for all visible planets and stars
    - HELIACAL_SETTING: evening last, for all visible planets and stars
    - EVENING_FIRST: evening first, for Mercury, Venus, Moon
    - MORNING_LAST: morning last, for Mercury, Venus, Moon
 - flags: bit flags for ephemeris, and also:
    - HELFLAG_OPTICAL_PARAMS: for optical instruments
    - HELFLAG_NO_DETAILS: provide date, without details
    - HELFLAG_VISLIM_DARK: behave as if Sun is at nadir
    - HELFLAG_VISLIM_NOMOON: behave as if Moon is at nadir, i.e. the Moon as
      a factor disturbing the observation is excluded, useful if one is not
      interested in the heliacal date of that particular year, but in the
      heliacal date of that epoch
 
:Return: (dret)
 
 - dret: tuple of 3 Julian days:
    - 0: start visibility
    - 1: optimum visibility, 0 if flags >= HELFLAG_AV
    - 2: end of visibility, 0 if flags >= HELFLAG_AV
 
It works between geographic latitudes 60s - 60n.
 
Default values for ``atmo``: If this is too much for you, set all these values to 0. The software will then set the following defaults: Pressure 1013.25, temperature 15, relative humidity 40. The values will be modified depending on the altitude of the observer above sea level. If the extinction coefficient (meteorological range) ``datm[3]`` is 0, the software will calculate its value from ``datm[0..2]``.
 
This function raises swisseph.Error in case of fatal error.
helio_cross(...)
Compute a planet heliocentric crossing over some longitude (ET).
 
:Args: int planet, float x2cross, float tjdet, int flags=FLG_SWIEPH, bool backwards=False
 
 - planet: planet number
 - x2cross: longitude to search
 - tjdet: start time of search, as Julian day number, Ephemeris Time
 - flags: bit flags indicating what computation is wanted
 - backwards: a boolean indicating if we search back in time
 
:Return: float jdcross
 
 - jdcross: Julian day found
 
This function raises swisseph.Error in case of fatal error.
helio_cross_ut(...)
Compute a planet heliocentric crossing over some longitude (UT).
 
:Args: int planet, float x2cross, float tjdut, int flags=FLG_SWIEPH, bool backwards=False
 
 - planet: planet number
 - x2cross: longitude to search
 - tjdut: start time of search, as Julian day number, Universal Time
 - flags: bit flags indicating what computation is wanted
 - backwards: a boolean indicating if we search back in time
 
:Return: float jdcross
 
 - jdcross: Julian day found
 
This function raises swisseph.Error in case of fatal error.
house_name(...)
Get the name of a house method.
 
:Args: bytes hsys
 
 - hsys: house system identifier (1 byte)
 
:Return: str hsysname
 
 - hsysname: house system name, empty string if not found
house_pos(...)
Calculate house position of a body.
 
:Args: float armc, float geolat, float eps, seq objcoord, bytes hsys=b'P'
 
 - armc: ARMC
 - geolat: geographic latitude, in degrees (northern positive)
 - eps: obliquity, in degrees
 - objcoord: a sequence for ecl. longitude and latitude of the planet,
   in degrees
 - hsys: house method identifier (1 byte)
 
:Return: float hpos
 
 - hpos: value in [1:13[ (Gauquelin: [1:37[) indicating the house position
 
This function raises swisseph.Error in case of fatal error.
houses(...)
Calculate houses cusps (UT).
 
:Args: float tjdut, float lat, float lon, bytes hsys=b'P'
 
 - tjdut: input time, Julian day number, Universal Time
 - lat: geographic latitude, in degrees (northern positive)
 - lon: geographic longitude, in degrees (eastern positive)
 - hsys: house method identifier (1 byte)
 
:Return: (cusps), (ascmc)
 
 - cusps: tuple of 12 float for cusps (except Gauquelin: 36 float)
 - ascmc: tuple of 8 float for additional points
 
This function raises swisseph.Error in case of fatal error.
houses_armc(...)
Calculate houses cusps with ARMC.
 
:Args: float armc, float lat, float eps, bytes hsys=b'P', float ascmc9=0.0
 
 - armc: ARMC
 - lat: geographic latitude, in degrees (northern positive)
 - eps: obliquity, in degrees
 - hsys: house method identifier (1 byte)
 - ascmc9: optional parameter for Sunshine house system
 
:Return: (cusps), (ascmc)
 
 - cusps: tuple of 12 float for cusps (except Gauquelin: 36 float)
 - ascmc: tuple of 8 float for additional points
 
This function raises swisseph.Error in case of fatal error.
houses_armc_ex2(...)
Calculate houses cusps and their speeds with ARMC.
 
:Args: float armc, float lat, float eps, bytes hsys=b'P', float ascmc9=0.0
 
 - armc: ARMC
 - lat: geographic latitude, in degrees (northern positive)
 - eps: obliquity, in degrees
 - hsys: house method identifier (1 byte)
 - ascmc9: optional parameter for Sunshine house system
 
:Return: (cusps), (ascmc), (cuspsspeed), (ascmcspeed)
 
 - cusps: tuple of 12 float for cusps (except Gauquelin: 36 float)
 - ascmc: tuple of 8 float for additional points
 - cuspsspeed: tuple of 12 float for cusps speeds
 - ascmcspeed: tuple of 8 float for speeds of additional points
 
This function raises swisseph.Error in case of fatal error.
houses_ex(...)
Calculate houses cusps (extended) (UT).
 
:Args: float tjdut, float lat, float lon, bytes hsys=b'P', int flags=0
 
 - tjdut: input time, Julian day number, Universal Time
 - lat: geographic latitude, in degrees (northern positive)
 - lon: geographic longitude, in degrees (eastern positive)
 - hsys: house method identifier (1 byte)
 - flags: ephemeris flag, etc
 
:Return: (cusps), (ascmc)
 
 - cusps: tuple of 12 float for cusps (except Gauquelin: 36 float)
 - ascmc: tuple of 8 float for additional points
 
This function raises swisseph.Error in case of fatal error.
houses_ex2(...)
Calculate houses cusps and cusps speeds (UT).
 
:Args: float tjdut, float lat, float lon, bytes hsys=b'P', int flags=0
 
 - tjdut: input time, Julian day number, Universal Time
 - lat: geographic latitude, in degrees (northern positive)
 - lon: geographic longitude, in degrees (eastern positive)
 - hsys: house method identifier (1 byte)
 - flags: ephemeris flag, etc
 
:Return: (cusps), (ascmc), (cuspsspeed), (ascmcspeed)
 
 - cusps: tuple of 12 float for cusps (except Gauquelin: 36 float)
 - ascmc: tuple of 8 float for additional points
 - cuspsspeed: tuple of 12 float for cusps speeds
 - ascmcspeed: tuple of 8 float for speeds of additional points
 
This function raises swisseph.Error in case of fatal error.
jdet_to_utc(...)
Convert ET Julian day number to UTC.
 
:Args: float tjdet, int cal=GREG_CAL
 
 - tjdet: Julian day number in ET (TT)
 - cal: calendar flag, either GREG_CAL or JUL_CAL
 
:Return: int year, int month, int day, int hour, int mins, float secs
 
 - year, month, day: returned date
 - hour, mins, secs: returned time
 
This function raises ValueError if cal is not GREG_CAL or JUL_CAL.
jdut1_to_utc(...)
Convert UT1 Julian day number to UTC.
 
:Args: float tjdut, int cal=GREG_CAL
 
 - tjdut: Julian day number, in UT (UT1)
 - cal: either GREG_CAL or JUL_CAL
 
:Return: int year, int month, int day, int hour, int mins, float secs
 
 - year, month, day: returned date
 - hour, mins, secs: returned time
 
This function raises ValueError if cal is not GREG_CAL or JUL_CAL.
julday(...)
Calculate a Julian day number.
 
:Args: int year, int month, int day, float hour=12.0, int cal=GREG_CAL
 
 - year, month, day: the date
 - hour: the time of day, decimal with fraction
 - cal: either GREG_CAL (gregorian) or JUL_CAL (julian)
 
:Return: float jd
 
This function raises ValueError if cal is not GREG_CAL or JUL_CAL.
lat_to_lmt(...)
Translate local apparent time (LAT) to local mean time (LMT).
 
:Args: float tjdlat, float geolon
 
 - tjdlat: Julian day number, local apparent time
 - geolon: geographic longitude, in degrees (eastern positive)
 
:Return: float tjdlmt
 
 - tjdlmt: returned Julian day number, local mean time
 
This function raises swisseph.Error in case of fatal error.
lmt_to_lat(...)
Translate local mean time (LMT) to local apparent time (LAT).
 
:Args: float tjdlmt, float geolon
 
 - tjdlmt: Julian day number, local mean time
 - geolon: geographic longitude, in degrees (eastern positive)
 
:Return: float tjdlat
 
 - tjdlat: returned Julian day number, local apparent time
 
This function raises swisseph.Error in case of fatal error.
lun_eclipse_how(...)
Calculate attributes of a lunar eclipse (UTC).
 
:Args: float tjdut, seq geopos, int flags=FLG_SWIEPH
 
 - tjdut: input time, Julian day number, Universal Time
 - geopos: a sequence with:
    - geographic longitude, in degrees (eastern positive)
    - geographic latitude, in degrees (northern positive)
    - geographic altitude above sea level, in meters
 - flags: ephemeris flag, etc
 
:Return: int retflag, (attr)
 
 - retflag: returned bit flags:
    - 0 if there is no eclipse
    - SE_ECL_TOTAL or ECL_PENUMBRAL or ECL_PARTIAL
 - attr: tuple of 20 float, of which:
    - 0: umbral magnitude at tjd
    - 1: penumbral magnitude
    - 2: ?
    - 3: ?
    - 4: azimuth of moon at tjd
    - 5: true altitude of moon above horizon at tjd
    - 6: apparent altitude of moon above horizon at tjd
    - 7: distance of moon from opposition in degrees
    - 8: eclipse magnitude (equals attr[0])
    - 9: saros series number (if available, otherwise -99999999)
    - 10: saros series member number (if available, otherwise -99999999)
 
This function raises swisseph.Error in case of fatal error.
lun_eclipse_when(...)
Find the next lunar eclipse globally (UT).
 
:Args: float tjdut, int flags=FLG_SWIEPH, int ecltype=0, bool backwards=False
 
 - tjdut: input time, Julian day number, Universal Time
 - flags: ephemeris flag
 - ecltype: bit flags for eclipse type wanted:
    - ECL_TOTAL ECL_PARTIAL ECL_PENUMBRAL
    - ECL_ALLTYPES_LUNAR or 0 for any type
 - backwards: boolean, set to True to search back in time
 
:Return: int retflag, (tret)
 
 - retflag: returned bit flag:
    - ECL_TOTAL ECL_PARTIAL ECL_PENUMBRAL
 - tret: tuple of 10 float, of which:
    - 0: time of maximum eclipse
    - 1: ?
    - 2: time of partial phase begin (indices consistent with solar eclipses)
    - 3: time of partial phase end
    - 4: time of totality begin
    - 5: time of totality end
    - 6: time of penumbral phase begin
    - 7: time of penumbral phase end
 
This function raises swisseph.Error in case of fatal error.
lun_eclipse_when_loc(...)
Find the next lunar eclipse observable from a given geographic position (UT).
 
:Args: float tjdut, seq geopos, int flags=FLG_SWIEPH, bool backwards=False
 
 - tjdut: input time, Julian day number, Universal Time
 - geopos: a sequence with:
    - geographic longitude, in degrees (eastern positive)
    - geographic latitude, in degrees (northern positive)
    - geographic altitude, in meters above sea level
 - flags: ephemeris flag, etc
 - backwards: boolean, set to True to search back in time
 
:Return: int retflag, (tret), (attr)
 
 - retflag: returned bit flags:
    - ECL_TOTAL or ECL_PENUMBRAL or ECL_PARTIAL
 - tret: tuple of 10 float, of which:
    - 0: time of maximum eclipse
    - 1: ?
    - 2: time of partial phase begin (indices consistent with solar eclipses)
    - 3: time of partial phase end
    - 4: time of totality begin
    - 5: time of totality end
    - 6: time of penumbral phase begin (eclipse begin)
    - 7: time of penumbral phase end (eclipse end)
    - 8: time of moonrise, if it occurs during the eclipse
    - 9: time of moonset, if it occurs during the eclipse
 - attr: tuple of 20 float, of which:
    - 0: umbral magnitude at tjd
    - 1: penumbral magnitude
    - 2: ?
    - 3: ?
    - 4: azimuth of moon at tjd
    - 5: true altitude of moon above horizon at tjd
    - 6: apparent altitude of moon above horizon at tjd
    - 7: distance of moon from opposition in degrees (separation angle)
    - 8: umbral magnitude at tjd (equals attr[0])
    - 9: saros series number (if available; otherwise -99999999)
    - 10: saros series member number (if available; otherwise -99999999)
 
This function raises swisseph.Error in case of fatal error.
lun_occult_when_glob(...)
Find the next occultation of a planet or star by the moon globally (UT).
 
:Args: float tjdut, int or str body, int flags=FLG_SWIEPH, int ecltype=0, bool backwards=False
 
 - tjdut: input time, Julian day number, Universal Time
 - body: planet identifier (int) or star name (str)
 - flags: ephemeris flag, eventually ECL_ONE_TRY, etc
 - ecltype: bit flags for eclipse type wanted:
    - ECL_CENTRAL ECL_NONCENTRAL ECL_TOTAL ECL_ANNULAR ECL_PARTIAL
    - ECL_ANNULAR_TOTAL (equals ECL_HYBRID)
    - 0 for any type
 - backwards: boolean, set to True to search back in time
 
:Return: int retflags, (tret)
 
 - retflags: returned bit flags:
    - 0 if no occultation or eclipse found
    - ECL_TOTAL or ECL_ANNULAR or ECL_PARTIAL or ECL_ANNULAR_TOTAL    - ECL_CENTRAL
    - ECL_NONCENTRAL
 - tret: tuple of 10 float, of which:
    - 0: time of maximum occultation/eclipse
    - 1: time when occultation takes place at local apparent noon
    - 2: time of occultation begin
    - 3: time of occultation end
    - 4: time of of totality begin
    - 5: time of totality end
    - 6: time of center line begin
    - 7: time of center line end
    - 8: time when annular-total occultation becomes total
    - 9: time when annular-total occultation becomes annular again
 
This function raises swisseph.Error in case of fatal error.
 
If you want to have only one conjunction of the moon with the body tested, add the following flag: ECL_ONE_TRY. If this flag is not set, the function will search for an occultation until it finds one. For bodies with ecliptical latitudes > 5, the function may search successlessly until it reaches the end of the ephemeris.
lun_occult_when_loc(...)
Find next occultation of a planet or star by the moon for a given geographic position (UT).
 
:Args: float tjdut, int or str body, seq geopos, int flags=FLG_SWIEPH, bool backwards=False
 
 - tjdut: input time, Julian day number, Universal Time
 - body: planet identifier (int) or star name (str)
 - geopos: a sequence with:
    - geographic longitude, in degrees (eastern positive)
    - geographic latitude, in degrees (northern positive)
    - geographic altitude above sea level, in meters
 - flags: ephemeris flag, eventually ECL_ONE_TRY, etc
 - backwards: boolean, set to True for search back in time
 
:Return: int retflags, (tret), (attr)
 
 - retflags: returned bit flags:
    - 0 if no occultation or eclipse found
    - ECL_TOTAL or ECL_ANNULAR or ECL_PARTIAL,
    - ECL_VISIBLE, ECL_MAX_VISIBLE, ECL_1ST_VISIBLE, ECL_2ND_VISIBLE,
      ECL_3RD_VISIBLE, ECL_4TH_VISIBLE
 - tret: tuple of 10 float, of which:
    - 0: time of maximum occultation
    - 1: time of first contact
    - 2: time of second contact
    - 3: time of third contact
    - 4: time of fourth contact
 - attr: tuple of 20 float, of which:
    - 0: fraction of planet diameter covered by moon (magnitude)
    - 1: ratio of lunar diameter to planet one
    - 2: fraction of planet disc covered by moon (obscuration)
    - 3: diameter of core shadow in km
    - 4: azimuth of planet at tjd
    - 5: true altitude of planet above horizon at tjd
    - 6: apparent altitude of planet above horizon at tjd
    - 7: elongation of moon in degrees (separation angle)
 
This function raises swisseph.Error in case of fatal error.
 
If you want to have only one conjunction of the moon with the body tested, add the following flag: ECL_ONE_TRY. If this flag is not set, the function will search for an occultation until it finds one. For bodies with ecliptical latitudes > 5, the function may search successlessly until it reaches the end of the ephemeris.
lun_occult_where(...)
Find where a lunar occultation is central or maximal (UT).
 
:Args: float tjdut, int or str body, int flags=FLG_SWIEPH
 
 - tjdut: input time, Julian day number, Universal Time
 - body: planet identifier (int) or star name (str)
 - flags: ephemeris flag
 
:Return: int retflags, (geopos), (attr)
 
 - retflags: returned bit flags:
    - 0 if there is no occultation at tjd
    - ECL_TOTAL
    - ECL_ANNULAR
    - ECL_TOTAL | ECL_CENTRAL
    - ECL_TOTAL | ECL_NONCENTRAL
    - ECL_ANNULAR | ECL_CENTRAL
    - ECL_ANNULAR | ECL_NONCENTRAL
    - ECL_PARTIAL
 - geopos: tuple of 10 float, of which:
    - 0: geographic longitude of central line
    - 1: geographic latitude of central line
    - 2: geographic longitude of northern limit of umbra
    - 3: geographic latitude of northern limit of umbra
    - 4: geographic longitude of southern limit of umbra
    - 5: geographic latitude of southern limit of umbra
    - 6: geographic longitude of northern limit of penumbra
    - 7: geographic latitude of northern limit of penumbra
    - 8: geographic longitude of southern limit of penumbra
    - 9: geographic latitude of southern limit of penumbra
 - attr: tuple of 20 float, of which:
    - 0: fraction of object's diameter covered by moon (magnitude)
    - 1: ratio of lunar diameter to object's diameter
    - 2: fraction of object's disc covered by moon (obscuration)
    - 3: diameter of core shadow in km
    - 4: azimuth of object at tjd
    - 5: true altitude of object above horizon at tjd
    - 6: apparent altitude of object above horizon at tjd
    - 7: angular distance of moon from object in degrees
 
This function raises swisseph.Error in case of fatal error.
mooncross(...)
Compute Moon crossing over some longitude (ET).
 
:Args: float x2cross, float tjdet, int flags=FLG_SWIEPH
 
 - x2cross: longitude to search
 - tjdet: start time of search, Julian day number, Ephemeris Time
 - flags: bit flags indicating what computation is wanted
 
:Return: float jd_cross
 
 - jd_cross: Julian day number found
 
This function raises swisseph.Error in case of fatal error.
mooncross_node(...)
Compute next Moon crossing over node, by finding zero latitude crossing (ET).
 
:Args: float tjdet, int flags=FLG_SWIEPH
 
 - tjdet: start time of search, Julian day number, Ephemeris Time
 - flags: bit flags indicating what computation is wanted
 
:Return: float jd_cross, xlon, xlat
 
 - jd_cross: Julian day number found
 - xlon: Moon longitude found
 - xlat: Moon latitude found
 
This function raises swisseph.Error in case of fatal error.
mooncross_node_ut(...)
Compute next Moon crossing over node, by finding zero latitude crossing (UT).
 
:Args: float tjdut, int flags=FLG_SWIEPH
 
 - tjdut: start time of search, Julian day number, Universal Time
 - flags: bit flags indicating what computation is wanted
 
:Return: float jd_cross, xlon, xlat
 
 - jd_cross: Julian day number found
 - xlon: Moon longitude found
 - xlat: Moon latitude found
 
This function raises swisseph.Error in case of fatal error.
mooncross_ut(...)
Compute Moon crossing over some longitude (UT).
 
:Args: float x2cross, float tjdut, int flags=FLG_SWIEPH
 
 - x2cross: longitude to search
 - tjdut: start time of search, Julian day number, Universal Time
 - flags: bit flags indicating what computation is wanted
 
:Return: float jd_cross
 
 - jd_cross: Julian day number found
 
This function raises swisseph.Error in case of fatal error.
nod_aps(...)
Calculate planetary nodes and apsides (ET).
 
:Args: float tjdet, int planet, int method=NODBIT_MEAN, int flags=FLG_SWIEPH|FLG_SPEED
 
 - tjdet: input time, Julian day number, Ephemeris Time
 - planet: identifer of planet or object
 - method: bit flags NODBIT_MEAN, NODBIT_OSCU, NODBIT_OSCU_BAR, NODBIT_FOPOINT
 - flags: bit flags indicating what type of computation is wanted
 
:Return: (xnasc)(xndsc)(xperi)(xaphe)
 
 - xnasc: tuple of 6 float for ascending node
 - xndsc: tuple of 6 float for descending node
 - xperi: tuple of 6 float for perihelion
 - xaphe: tuple of 6 float for aphelion
 
This function can raise swisseph.Error in case of fatal error.
nod_aps_ut(...)
Calculate planetary nodes and apsides (UT).
 
:Args: float tjdut, int planet, int method=NODBIT_MEAN, int flags=FLG_SWIEPH|FLG_SPEED
 
 - tjdut: input time, Julian day number, Universal Time
 - planet: identifer of planet or object
 - method: bit flags NODBIT_MEAN, NODBIT_OSCU, NODBIT_OSCU_BAR, NODBIT_FOPOINT
 - flags: bit flags indicating what type of computation is wanted
 
:Return: (xnasc)(xndsc)(xperi)(xaphe)
 
 - xnasc: tuple of 6 float for ascending node
 - xndsc: tuple of 6 float for descending node
 - xperi: tuple of 6 float for perihelion
 - xaphe: tuple of 6 float for aphelion
 
This function can raise swisseph.Error in case of fatal error.
orbit_max_min_true_distance(...)
Calculate the maximum possible distance, the minimum possible distance, and the current true distance of planet, the EMB, or an asteroid.
 
:Args: float tjdet, int planet, int flags
 
 - tjdet: input time, Julian day number, Ephemeris Time
 - planet: identifier of planet or object
 - flags: bit flags indicating what computation is wanted:
    - ephemeris flag
    - optional heliocentric flag FLG_HELIOCTR
 
:Return: float max_dist, float min_dist, float true_dist
 
 - max_dist: maximum distance
 - min_dist: minimum_distance
 - true_dist: true distance
pheno(...)
Calculate planetary phenomena (ET).
 
:Args: float tjdet, int planet, int flags=FLG_SWIEPH
 
 - tjdet: input time, Julian day number, Ephemeris Time
 - planet: object identifier
 - flags: ephemeris flag, etc
 
:Return: (attr)
 
 - attr: tuple of 20 float, of which:
    - 0: phase angle (earth-planet-sun)
    - 1: phase (illuminated fraction of disc)
    - 2: elongation of planet
    - 3: apparent diameter of disc
    - 4: apparent magnitude
    - 5: geocentric horizontal parallax (Moon)
 
This function raises swisseph.Error in case of fatal error.
pheno_ut(...)
Calculate planetary phenomena (UT).
 
:Args: float tjdut, int planet, int flags=FLG_SWIEPH
 
 - tjdut: input time, Julian day number, Universal Time
 - planet: object identifier
 - flags: ephemeris flag, etc
 
:Return: (attr)
 
 - attr: tuple of 20 float, of which:
    - 0: phase angle (earth-planet-sun)
    - 1: phase (illuminated fraction of disc)
    - 2: elongation of planet
    - 3: apparent diameter of disc
    - 4: apparent magnitude
    - 5: geocentric horizontal parallax (Moon)
 
This function raises swisseph.Error in case of fatal error.
rad_midp(...)
Calculate midpoint (in radians).
 
Args: float x, float y
Return: float
radnorm(...)
Normalization of any radian number to the range [0;2*pi].
 
Args: float x
Return: float
refrac(...)
Calculate true altitude from apparent altitude, or vice-versa.
 
:Args: float alt, float atpress, float attemp, int flag
 
 - alt: altitude of object above geometric horizon in degrees,
   where geometric horizon = plane perpendicular to gravity
 - atpress: atmospheric pressure in mbar (hPa)
 - attemp: atmospheric temperature in degrees Celsius
 - flag: either TRUE_TO_APP or APP_TO_TRUE
 
:Return: float retalt
 
 - retalt: converted altitude
refrac_extended(...)
Calculate true altitude from apparent altitude, or vice-versa (extended).
 
:Args: float alt, float geoalt, float atpress, float attemp, float lapserate, int flag
 
 - alt: altitude of object above geometric horizon in degrees,
   where geometric horizon = plane perpendicular to gravity
 - geoalt: altitude of observer above sea level, in meters
 - atpress: atmospheric pressure in mbar (hPa)
 - attemp: atmospheric temperature in degrees Celsius
 - lapserate: dattemp/dgeoalt [deg K/m]
 - flag: either TRUE_TO_APP or APP_TO_TRUE
 
:Return: float retalt, (dret)
 
 - retalt: converted altitude
 - dret: tuple of 4 float:
    - 0: true altitude if possible, otherwise input value
    - 1: apparent altitude if possible, otherwise input value
    - 2: refraction
    - 3: dip of the horizon
revjul(...)
Calculate year, month, day, hour from Julian day number.
 
:Args: float jd, int cal=GREG_CAL
 
 - jd: Julian day number
 - cal: either GREG_CAL (gregorian) or JUL_CAL (julian)
 
:Return: int year, int month, int day, float hour
 
This function raises ValueError if cal is not GREG_CAL or JUL_CAL.
rise_trans(...)
Calculate times of rising, setting and meridian transits.
 
:Args: float tjdut, int or str body, int rsmi, seq geopos, float atpress=0.0, float attemp=0.0, int flags=FLG_SWIEPH
 
 - tjdut: input time, Julian day number, Universal Time
 - body: planet identifier (int) or fixed star name (str)
 - rsmi: bit flag for rise, set, or one of the two meridian transits, etc
 - geopos: a sequence for:
    - 0: geographic longitude, in degrees (eastern positive)
    - 1: geographic latitude, in degrees (northern positive)
    - 2: geographic altitude, in meters above sea level
 - atpress: atmospheric pressure in mbar/hPa
 - attemp: atmospheric temperature in degrees Celsius
 - flags: ephemeris flags etc
 
:Return: int res, (tret)
 
 - res: integer indicating:
    - (0) event found
    - (-2) event not found because the object is circumpolar
 - tret: tuple of 10 float, of which:
    - 0: tjd of event
 
This function raises swisseph.Error in case of fatal error.
rise_trans_true_hor(...)
Calculate times of rising, setting and meridian transits (with altitude).
 
:Args: float tjdut, int or str body, int rsmi, seq geopos, float atpress=0.0, float attemp=0.0, float horhgt=0.0, int flags=FLG_SWIEPH
 
 - tjdut: input time, Julian day number, Universal Time
 - body: planet identifier (int) or fixed star name (str)
 - rsmi: bit flag for rise, set, or one of the two meridian transits, etc
 - geopos: a sequence for:
    - 0: geographic longitude (eastern positive)
    - 1: geographic latitude (northern positive)
    - 2: altitude above sea level, in meters
 - atpress: atmospheric pressure in mbar/hPa
 - attemp: atmospheric temperature in degrees Celsius
 - horhgt: height of local horizon in degrees (where body rises or sets)
 - flags: ephemeris flags etc
 
:Return: int res, (tret)
 
 - res: integer indicating:
    - 0 event found
    - -2 event not found because the object is circumpolar
 - tret: tuple of 10 float, of which:
    - 0: tjd of event
 
This function raises swisseph.Error in case of fatal error.
set_delta_t_userdef(...)
Set a fixed Deltat T value.
 
:Args: acc
:Return: None
 
This function allows the user to set a fixed Delta T value that will be returned by ``deltat()`` or ``deltat_ex()``. The same Delta T value will then be used by ``calc_ut()``, eclipse functions, heliacal functions, and all functions that require UT as input time.
 
In order to return to automatic Delta T, call this function with the following value: ``set_delta_t_userdef(DELTAT_AUTOMATIC)``.
set_ephe_path(...)
Set ephemeris files path.
 
:Args: str path="/usr/share/libswe:/usr/local/share/libswe"
:Return: None
 
It is possible to pass None as path, which is equivalent to an empty string.
set_jpl_file(...)
Set name of JPL ephemeris file.
 
:Args: str name
:Return: None
 
If you work with the JPL ephemeris, SwissEph uses the default file name which is defined as ``FNAME_DFT``. Currently, it has the value ``de406.eph`` or ``de431.eph``.
 
If a different JPL ephemeris file is required, call this function to make the file name known to the software, eg::
 
    swe.set_jpl_file('de405.eph')
 
This file must reside in the ephemeris path you are using for all your ephemeris files.
set_lapse_rate(...)
Set lapse rate.
 
:Args: float lrate
:Return: None
set_sid_mode(...)
Set sidereal mode.
 
:Args: int sidmode, float t0=0.0, float ayan_t0=0.0
:Return: None
 
This function can be used to specify the mode for sidereal computations. ``calc()`` or ``fixstar()`` has then to be called with the bit ``FLG_SIDEREAL``.
 
If ``set_sid_mode()`` is not called, the default ayanamsha (Fagan/Bradley) is used.
 
If a predefined mode is wanted, the parameter ``sidmode`` has to be set, while ``t0`` and ``ayan_t0`` are not considered, i.e. can be 0.
 
For information about the sidereal modes, please read the chapter on sidereal calculations in the documentation.
set_tid_acc(...)
Set value of the tidal acceleration.
 
:Args: float acc
 
 - acc: the values possible are:
    - TIDAL_DE200
    - TIDAL_DE403
    - TIDAL_DE404
    - TIDAL_DE405
    - TIDAL_DE406
    - TIDAL_DE421
    - TIDAL_DE422
    - TIDAL_DE430
    - TIDAL_DE431
    - TIDAL_DE441
    - TIDAL_26
    - TIDAL_STEPHENSON_2016
    - TIDAL_DEFAULT (equals TIDAL_DE431)
    - TIDAL_MOSEPH (equals TIDAL_DE404)
    - TIDAL_SWIEPH (equals TIDAL_DEFAULT)
    - TIDAL_JPLEPH (equals TIDAL_DEFAULT)
 
:Return: None
 
With Swiss Ephemeris versions until 1.80, this function had always to be used, if a nonstandard ephemeris like DE200 or DE421 was used.
 
Since Swiss Ephemeris version 2.00, this function is usually not needed, because the value is automatically set according to the ephemeris files selected or available. However, under certain circumstances that are described in the documentation section for ``swe_deltat()``, the user may want to control the tidal acceleration himself.
 
Once the function ``set_tid_acc()`` has been used, the automatic setting of tidal acceleration is blocked. In order to unblock it again, call ``set_tid_acc(TIDAL_AUTOMATIC)``.
set_topo(...)
Set topocentric parameters.
 
:Args: float lon, float lat, float alt=0.0
 
 - lon: geographic longitude, in degrees (eastern positive)
 - lat: geographic latitude, in degrees (northern positive)
 - alt: geographic altitude in meters above sea level
 
:Return: None
sidtime(...)
Calculate sidereal time (UT).
 
:Args: float tjdut
 
 - tjdut: input time, Julian day number, Universal Time
 
:Return: float sidtime
sidtime0(...)
Calculate sidereal time, given obliquity and nutation (UT).
 
:Args: float tjdut, float eps, float nutation
 
 - tjdut: input time, Julian day number, Universal Time
 - eps: obliquity, in degrees
 - nutation: nutation in longitude, in degrees
 
:Return: float sidtime
sol_eclipse_how(...)
Calculate attributes of a solar eclipse for a given geographic position and time.
 
:Args: float tjdut, seq geopos, int flags=FLG_SWIEPH
 
 - tjdut: input time, Julian day number, Universal Time
 - geopos: a sequence with:
    - geographic longitude, in degrees (eastern positive)
    - geographic latitude, in degrees (northern positive)
    - geographic altitude above sea level, in meters
 
 - flags: ephemeris flag, etc
 
:Return: int retflags, (attr)
 
 - retflags: returned bit flags:
    - 0 if no eclipse is visible at position
    - ECL_TOTAL ECL_ANNULAR ECL_PARTIAL
 - attr: tuple of 20 float, of which:
    - 0: fraction of solar diameter covered by moon
    - 1: ratio of lunar diameter to solar one
    - 2: fraction of solar disc covered by moon (obscuration)
    - 3: diameter of core shadow in km
    - 4: azimuth of sun at tjd
    - 5: true altitude of sun above horizon at tjd
    - 6: apparent altitude of sun above horizon at tjd
    - 7: elongation of moon in degrees (separation angle)
    - 8: magnitude acc. to NASA (equals attr[0] for partial and attr[1] for      annular and total eclipses)
    - 9: saros series number (if available, otherwise -99999999)
    - 10: saros series member number (if available, otherwise -99999999)
 
This function raises swisseph.Error in case of fatal error.
sol_eclipse_when_glob(...)
Find the next solar eclipse globally (UT).
 
:Args: float tjdut, int flags=FLG_SWIEPH, int ecltype=0, bool backwards=False
 
 - tjdut: input time, Julian day number, Universal Time
 - flags: ephemeris flag
 - ecltype: bit flags for eclipse type wanted:
    - ECL_CENTRAL ECL_NONCENTRAL ECL_TOTAL ECL_ANNULAR ECL_PARTIAL
    - ECL_ANNULAR_TOTAL (equals ECL_HYBRID)
    - ECL_ALLTYPES_SOLAR or 0 for any type
 - backwards: boolean, set to True to search back in time
 
:Return: int res, (tret)
 
 - res: returned bit flags:
    - ECL_TOTAL ECL_ANNULAR ECL_PARTIAL ECL_ANNULAR_TOTAL
    - ECL_CENTRAL
    - ECL_NONCENTRAL
 
 - tret: tuple of 10 float, of which:
    - 0: time of maximum eclipse
    - 1: time when eclipse takes place at local apparent noon
    - 2: time of eclipse begin
    - 3: time of eclipse end
    - 4: time of totality begin
    - 5: time of totality end
    - 6: time of center line begin
    - 7: time of center line end
    - 8: time when annular-total eclipse becomes total
    - 9: time when annular-total eclipse becomes annular again
 
This function raises swisseph.Error in case of fatal error.
sol_eclipse_when_loc(...)
Find the next solar eclipse for a given geographic position (UT).
 
:Args: float tjdut, seq geopos, int flags=FLG_SWIEPH, bool backwards=False
 
 - tjdut: input time, Julian day number, Universal Time
 - geopos: a sequence with:
    - geographic longitude, in degrees (eastern positive)
    - geographic latitude, in degrees (northern positive)
    - geographic altitude above sea level, in meters
 - flags: ephemeris flag, etc
 - backwards: boolean, set to True to search back in time
 
:Return: int retflags, (tret), (attr)
 
 - retflags: returned bit flags:
    - ECL_TOTAL or ECL_ANNULAR or ECL_PARTIAL,
    - ECL_VISIBLE, ECL_MAX_VISIBLE, ECL_1ST_VISIBLE, ECL_2ND_VISIBLE,
      ECL_3RD_VISIBLE, ECL_4TH_VISIBLE
 - tret: tuple of 10 float, of which:
    - 0: time of maximum eclipse
    - 1: time of first contact
    - 2: time of second contact
    - 3: time of third contact
    - 4: time of fourth contact
    - 5: time of sunrise between first and fourth contact
    - 6: time of sunset between first and fourth contact
 - attr: tuple of 20 float, of which:
    - 0: fraction of solar diameter covered by moon; with total/annular
      eclipse, it results in magnitude acc. to IMCCE.
    - 1: ratio of lunar diameter to solar one
    - 2: fraction of solar disc covered by moon (obscuration)
    - 3: diameter of core shadow in km
    - 4: azimuth of sun at tjd
    - 5: true altitude of sun above horizon at tjd
    - 6: apparent altitude of sun above horizon at tjd
    - 7: elongation of moon in degrees (separation angle)
    - 8: magnitude acc. to NASA (equals attr[0] for partial and attr[1] for      annular and total eclipses)
    - 9: saros series number (if available, otherwise -99999999)
    - 10: saros series member number (if available, otherwise -99999999)
 
This function raises swisseph.Error in case of fatal error.
sol_eclipse_where(...)
Find where a solar eclipse is central or maximal (UT).
 
:Args: float tjdut, int flags=FLG_SWIEPH
 
 - tjdut: input time, Julian day number, Universal Time
 - flags: ephemeris flag
 
:Return: int retflags, (geopos), (attr)
 
 - retflags: returned bit flags:
    - ECL_TOTAL
    - ECL_ANNULAR
    - ECL_TOTAL | ECL_CENTRAL
    - ECL_TOTAL | ECL_NONCENTRAL
    - ECL_ANNULAR | ECL_CENTRAL
    - ECL_ANNULAR | ECL_NONCENTRAL
    - ECL_PARTIAL
 - geopos: tuple of 10 float for longitude/latitude of:
    - 0: geographic longitude of central line
    - 1: geographic latitude of central line
    - 2: geographic longitude of northern limit of umbra
    - 3: geographic latitude of northern limit of umbra
    - 4: geographic longitude of southern limit of umbra
    - 5: geographic latitude of southern limit of umbra
    - 6: geographic longitude of northern limit of penumbra
    - 7: geographic latitude of northern limit of penumbra
    - 8: geographic longitude of southern limit of penumbra
    - 9: geographic latitude of southern limit of penumbra
 - attr: tuple of 20 float, of which:
    - 0: fraction of solar diameter covered by moon; with total/annular
      eclipse, it results in magnitude acc. to IMCCE.
    - 1: ratio of lunar diameter to solar one
    - 2: fraction of solar disc covered by moon
    - 3: diameter of core shadow in km
    - 4: azimuth of sun at tjd
    - 5: true altitude of sun above horizon at tjd
    - 6: apparent altitude of sun above horizon at tjd
    - 7: elongation of moon in degrees (separation angle)
    - 8: magnitude acc. to NASA (equals attr[0] for partial and attr[1] for      annular and total eclipses)
    - 9: saros series number (if available, otherwise -99999999)
    - 10: saros series member number (if available, otherwise -99999999)
 
This function raises swisseph.Error in case of fatal error.
solcross(...)
Compute next Sun crossing over some longitude (ET).
 
:Args: float x2cross, float tjdet, int flags=FLG_SWIEPH
 
 - x2cross: longitude to search
 - tjdet: start time of search, Julian day number, Ephemeris Time
 - flags: bit flags indicating what computation is wanted
 
:Return: float jdcross
 
 - jdcross: Julian day number found
 
This function raises swisseph.Error in case of fatal error.
solcross_ut(...)
Compute next Sun crossing over some longitude (UT).
 
:Args: float x2cross, float tjdut, int flags=FLG_SWIEPH
 
 - x2cross: longitude to search
 - tjdut: start time of search, Julian day number, Universal Time
 - flags: bit flags indicating what computation is wanted
 
:Return: float jdcross
 
 - jdcross: Julian day number found
 
This function raises swisseph.Error in case of fatal error.
split_deg(...)
Provide sign or nakshatra, degree, minutes, seconds and fraction of second from decimal degree. Can also round to seconds, minutes, degrees.
 
:Args: float degree, int roundflag
 
 - degree: position in decimal degrees
 - roundflag: bit flags combination indicating how to round:
    - 0: dont round
    - SPLIT_DEG_ROUND_SEC: round to seconds
    - SPLIT_DEG_ROUND_MIN: round to minutes
    - SPLIT_DEG_ROUND_DEG: round to degrees
    - SPLIT_DEG_ZODIACAL: with zodiac sign number
    - SPLIT_DEG_NAKSHATRA: with nakshatra number
    - SPLIT_DEG_KEEP_SIGN: dont round to next zodiac sign/nakshatra
    - SPLIT_DEG_KEEP_DEG: dont round to next degree
 
:Return: deg, min, sec, secfr, sign
 
 - deg: returned degree
 - min: returned minutes
 - sec: returned seconds
 - secfr: returned fraction of second
 - sign: returned sign/nakshatra number
time_equ(...)
Calculate equation of time (UT).
 
:Args: float tjdut
 
 - tjdut: input time, Julian day number, Universal Time
 
:Return: float e
 
 - e: difference between local apparent time and local mean time in days
 
This function raises swisseph.Error in case of fatal error.
utc_time_zone(...)
Transform local time to UTC or UTC to local time.
 
:Args: int year, int month, int day, int hour, int minutes, float seconds, float offset
 
 - year, month, day, hour, minutes, seconds: date and time
 - offset: timezone offset in hours (east of greenwich positive)
 
:Return: int retyear, retmonth, retday, rethour, retmin, float retsec
 
 - retyear, retmonth, retday: returned date
 - rethour, retmin, retsec: returned time
 
For conversion from local time to UTC, use +(offset). For conversion from UTC to local time, use -(offset).
utc_to_jd(...)
Convert UTC to julian day.
 
:Args: int year, int month, int day, int hour, int minutes, float seconds, int cal=GREG_CAL
 
 - year, month, day, hour, minutes, seconds: date and time
 - cal: either GREG_CAL or JUL_CAL
 
:Return: float jdet, float jdut
 
 - jdet: Julian day in ET (TT)
 - jdut: Julian day in UT (UT1)
 
This function raises ValueError if cal is not GREG_CAL or JUL_CAL.
It raises swisseph.Error in case of fatal error.
vis_limit_mag(...)
Find the limiting visual magnitude in dark skies.
 
:Args: float tjdut, seq geopos, seq atmo, seq observer, str objname, int flags
 
 - tjdut: input time, Julian day number, Universal Time
 - geopos: a sequence with:
    - 0: geographic longitude (eastern positive)
    - 1: geographic latitude (northern positive)
    - 2: altitude above sea level, in meters
 - atmo: a sequence with:
    - 0: atmospheric pressure in mbar (hPa)
    - 1: atmospheric temperature in degrees Celsius
    - 2: relative humidity in %
    - 3: if >= 1, Meteorological Range (km).
      Between 1 and 0, total atmospheric coefficient (ktot).
      If = 0, the other atmospheric parameters determine the total
      atmospheric coefficient (ktot)
 - observer: a sequence with:
    - 0: age of observer in years (default = 36)
    - 1: snellen ratio of observers eyes (default = 1 = normal)
    - The following parameters are only relevant if HELFLAG_OPTICAL_PARAMS
      is set:
    - 2: (0) = monocular, (1) = binocular (boolean)
    - 3: telescope magnification, (0) = default to naked eye (binocular),
      (1) = naked eye
    - 4: optical aperture (telescope diameter) in mm
    - 5: optical transmission
 - objname: name of planet or fixed star
 - flags: bit flags for ephemeris, and also:
    - HELFLAG_OPTICAL_PARAMS: for optical instruments
    - HELFLAG_NO_DETAILS: provide date, without details
    - HELFLAG_VISLIM_DARK: behave as if Sun is at nadir
    - HELFLAG_VISLIM_NOMOON: behave as if Moon is at nadir, i.e. the Moon as
      a factor disturbing the observation is excluded, useful if one is not
      interested in the heliacal date of that particular year, but in the
      heliacal date of that epoch
 
:Return: float res, (dret)
 
 - res: result:
    - (-2): object is below horizon
    - (0): OK, photopic vision
    - (1): OK, scotopic vision
    - (2): OK, near limit photopic/scotopic vision
 - dret: a tuple of 10 float, of which:
    - 0: limiting visual magnitude (if > magnitude of object, then the
      object is visible)
    - 1: altitude of object
    - 2: azimuth of object
    - 3: altitude of sun
    - 4: azimuth of sun
    - 5: altitude of moon
    - 6: azimuth of moon
    - 7: magnitude of object
 
This function raises swisseph.Error in case of fatal error.

 
Data
      	 	ACRONYCHAL_RISING = 5
ACRONYCHAL_SETTING = 6
ADMETOS = 45
APOLLON = 44
APP_TO_TRUE = 1
ARMC = 2
ASC = 0
ASTNAMFILE = 'seasnam.txt'
AST_OFFSET = 10000
AUNIT_TO_KM = 149597870.7
AUNIT_TO_LIGHTYEAR = 1.5812507409819728e-05
AUNIT_TO_PARSEC = 4.848136811095274e-06
BIT_ASTRO_TWILIGHT = 4096
BIT_CIVIL_TWILIGHT = 1024
BIT_DISC_BOTTOM = 8192
BIT_DISC_CENTER = 256
BIT_FIXED_DISC_SIZE = 16384
BIT_FORCE_SLOW_METHOD = 32768
BIT_HINDU_RISING = 896
BIT_NAUTIC_TWILIGHT = 2048
BIT_NO_REFRACTION = 512
CALC_ITRANSIT = 8
CALC_MTRANSIT = 4
CALC_RISE = 1
CALC_SET = 2
CERES = 17
CHIRON = 15
COASC1 = 5
COASC2 = 6
COMET_OFFSET = 1000
COSMICAL_SETTING = 6
CUPIDO = 40
DELTAT_AUTOMATIC = -1e-10
DE_NUMBER = 431
EARTH = 14
ECL2HOR = 0
ECL_1ST_VISIBLE = 512
ECL_2ND_VISIBLE = 1024
ECL_3RD_VISIBLE = 2048
ECL_4TH_VISIBLE = 4096
ECL_ALLTYPES_LUNAR = 84
ECL_ALLTYPES_SOLAR = 63
ECL_ANNULAR = 8
ECL_ANNULAR_TOTAL = 32
ECL_CENTRAL = 1
ECL_HYBRID = 32
ECL_MAX_VISIBLE = 256
ECL_NONCENTRAL = 2
ECL_NUT = -1
ECL_OCC_BEG_DAYLIGHT = 8192
ECL_OCC_END_DAYLIGHT = 16384
ECL_ONE_TRY = 32768
ECL_PARTBEG_VISIBLE = 512
ECL_PARTEND_VISIBLE = 4096
ECL_PARTIAL = 16
ECL_PENUMBBEG_VISIBLE = 8192
ECL_PENUMBEND_VISIBLE = 16384
ECL_PENUMBRAL = 64
ECL_TOTAL = 4
ECL_TOTBEG_VISIBLE = 1024
ECL_TOTEND_VISIBLE = 2048
ECL_VISIBLE = 128
EPHE_PATH = '.:/users/ephe2/:/users/ephe/'
EQU2HOR = 1
EQUASC = 4
EVENING_FIRST = 3
EVENING_LAST = 2
FICTFILE = 'seorbel.txt'
FICT_MAX = 999
FICT_OFFSET = 40
FICT_OFFSET_1 = 39
FIXSTAR = -10
FLG_ASTROMETRIC = 1536
FLG_BARYCTR = 16384
FLG_CENTER_BODY = 1048576
FLG_DEFAULTEPH = 2
FLG_DPSIDEPS_1980 = 262144
FLG_EQUATORIAL = 2048
FLG_HELCTR = 8
FLG_ICRS = 131072
FLG_J2000 = 32
FLG_JPLEPH = 1
FLG_JPLHOR = 262144
FLG_JPLHOR_APPROX = 524288
FLG_MOSEPH = 4
FLG_NOABERR = 1024
FLG_NOGDEFL = 512
FLG_NONUT = 64
FLG_ORBEL_AA = 32768
FLG_RADIANS = 8192
FLG_SIDEREAL = 65536
FLG_SPEED = 256
FLG_SPEED3 = 128
FLG_SWIEPH = 2
FLG_TEST_PLMOON = 2228280
FLG_TOPOCTR = 32768
FLG_TROPICAL = 0
FLG_TRUEPOS = 16
FLG_XYZ = 4096
FNAME_DE200 = 'de200.eph'
FNAME_DE403 = 'de403.eph'
FNAME_DE404 = 'de404.eph'
FNAME_DE405 = 'de405.eph'
FNAME_DE406 = 'de406.eph'
FNAME_DFT = 'de431.eph'
FNAME_DFT2 = 'de406.eph'
GREG_CAL = 1
HADES = 41
HARRINGTON = 50
HELFLAG_AV = 65536
HELFLAG_AVKIND = 983040
HELFLAG_AVKIND_MIN7 = 262144
HELFLAG_AVKIND_MIN9 = 524288
HELFLAG_AVKIND_PTO = 131072
HELFLAG_AVKIND_VR = 65536
HELFLAG_HIGH_PRECISION = 256
HELFLAG_LONG_SEARCH = 128
HELFLAG_NO_DETAILS = 1024
HELFLAG_OPTICAL_PARAMS = 512
HELFLAG_SEARCH_1_PERIOD = 2048
HELFLAG_VISLIM_DARK = 4096
HELFLAG_VISLIM_NOMOON = 8192
HELFLAG_VISLIM_PHOTOPIC = 16384
HELIACAL_RISING = 1
HELIACAL_SETTING = 2
HOR2ECL = 0
HOR2EQU = 1
INTP_APOG = 21
INTP_PERG = 22
ISIS = 48
JUL_CAL = 0
JUNO = 19
JUPITER = 5
KRONOS = 43
MARS = 4
MAX_STNAME = 256
MC = 1
MEAN_APOG = 12
MEAN_NODE = 10
MERCURY = 2
MIXEDOPIC_FLAG = 2
MODEL_BIAS = 4
MODEL_DELTAT = 0
MODEL_JPLHORA_MODE = 6
MODEL_JPLHOR_MODE = 5
MODEL_NUT = 3
MODEL_PREC_LONGTERM = 1
MODEL_PREC_SHORTTERM = 2
MODEL_SIDT = 7
MOD_BIAS_DEFAULT = 3
MOD_BIAS_IAU2000 = 2
MOD_BIAS_IAU2006 = 3
MOD_BIAS_NONE = 1
MOD_DELTAT_DEFAULT = 5
MOD_DELTAT_ESPENAK_MEEUS_2006 = 4
MOD_DELTAT_STEPHENSON_1997 = 2
MOD_DELTAT_STEPHENSON_ETC_2016 = 5
MOD_DELTAT_STEPHENSON_MORRISON_1984 = 1
MOD_DELTAT_STEPHENSON_MORRISON_2004 = 3
MOD_JPLHORA_1 = 1
MOD_JPLHORA_2 = 2
MOD_JPLHORA_3 = 3
MOD_JPLHORA_DEFAULT = 3
MOD_JPLHOR_DEFAULT = 1
MOD_JPLHOR_LONG_AGREEMENT = 1
MOD_NBIAS = 3
MOD_NDELTAT = 5
MOD_NJPLHOR = 2
MOD_NJPLHORA = 3
MOD_NNUT = 5
MOD_NPREC = 11
MOD_NUT_DEFAULT = 4
MOD_NUT_IAU_1980 = 1
MOD_NUT_IAU_2000A = 3
MOD_NUT_IAU_2000B = 4
MOD_NUT_IAU_CORR_1987 = 2
MOD_NUT_WOOLARD = 5
MOD_PREC_BRETAGNON_2003 = 7
MOD_PREC_DEFAULT = 9
MOD_PREC_DEFAULT_SHORT = 9
MOD_PREC_IAU_1976 = 1
MOD_PREC_IAU_2000 = 6
MOD_PREC_IAU_2006 = 8
MOD_PREC_LASKAR_1986 = 2
MOD_PREC_NEWCOMB = 11
MOD_PREC_OWEN_1990 = 10
MOD_PREC_SIMON_1994 = 5
MOD_PREC_VONDRAK_2011 = 9
MOD_PREC_WILLIAMS_1994 = 4
MOD_PREC_WILL_EPS_LASK = 3
MOON = 1
MORNING_FIRST = 1
MORNING_LAST = 4
NALL_NAT_POINTS = 38
NASCMC = 8
NEPTUNE = 8
NEPTUNE_ADAMS = 52
NEPTUNE_LEVERRIER = 51
NFICT_ELEM = 15
NIBIRU = 49
NODBIT_FOPOINT = 256
NODBIT_MEAN = 1
NODBIT_OSCU = 2
NODBIT_OSCU_BAR = 4
NPLANETS = 23
NSE_MODELS = 8
NSIDM_PREDEF = 47
OSCU_APOG = 13
PALLAS = 18
PHOLUS = 16
PHOTOPIC_FLAG = 0
PLMOON_OFFSET = 9000
PLUTO = 9
PLUTO_LOWELL = 53
PLUTO_PICKERING = 54
POLASC = 7
POSEIDON = 47
PROSERPINA = 57
SATURN = 6
SCOTOPIC_FLAG = 1
SE_FNAME_DE431 = 'de431.eph'
SIDBITS = 256
SIDBIT_ECL_DATE = 2048
SIDBIT_ECL_T0 = 256
SIDBIT_NO_PREC_OFFSET = 4096
SIDBIT_PREC_ORIG = 8192
SIDBIT_SSY_PLANE = 512
SIDBIT_USER_UT = 1024
SIDM_ALDEBARAN_15TAU = 14
SIDM_ARYABHATA = 23
SIDM_ARYABHATA_522 = 37
SIDM_ARYABHATA_MSUN = 24
SIDM_B1950 = 20
SIDM_BABYL_BRITTON = 38
SIDM_BABYL_ETPSC = 13
SIDM_BABYL_HUBER = 12
SIDM_BABYL_KUGLER1 = 9
SIDM_BABYL_KUGLER2 = 10
SIDM_BABYL_KUGLER3 = 11
SIDM_DELUCE = 2
SIDM_DJWHAL_KHUL = 6
SIDM_FAGAN_BRADLEY = 0
SIDM_GALALIGN_MARDYKS = 34
SIDM_GALCENT_0SAG = 17
SIDM_GALCENT_COCHRANE = 40
SIDM_GALCENT_MULA_WILHELM = 36
SIDM_GALCENT_RGILBRAND = 30
SIDM_GALEQU_FIORENZA = 41
SIDM_GALEQU_IAU1958 = 31
SIDM_GALEQU_MULA = 33
SIDM_GALEQU_TRUE = 32
SIDM_HIPPARCHOS = 15
SIDM_J1900 = 19
SIDM_J2000 = 18
SIDM_JN_BHASIN = 8
SIDM_KRISHNAMURTI = 5
SIDM_KRISHNAMURTI_VP291 = 45
SIDM_LAHIRI = 1
SIDM_LAHIRI_1940 = 43
SIDM_LAHIRI_ICRC = 46
SIDM_LAHIRI_VP285 = 44
SIDM_RAMAN = 3
SIDM_SASSANIAN = 16
SIDM_SS_CITRA = 26
SIDM_SS_REVATI = 25
SIDM_SURYASIDDHANTA = 21
SIDM_SURYASIDDHANTA_MSUN = 22
SIDM_TRUE_CITRA = 27
SIDM_TRUE_MULA = 35
SIDM_TRUE_PUSHYA = 29
SIDM_TRUE_REVATI = 28
SIDM_TRUE_SHEORAN = 39
SIDM_USER = 255
SIDM_USHASHASHI = 4
SIDM_VALENS_MOON = 42
SIDM_YUKTESHWAR = 7
SIMULATE_VICTORVB = 1
SPLIT_DEG_KEEP_DEG = 32
SPLIT_DEG_KEEP_SIGN = 16
SPLIT_DEG_NAKSHATRA = 1024
SPLIT_DEG_ROUND_DEG = 4
SPLIT_DEG_ROUND_MIN = 2
SPLIT_DEG_ROUND_SEC = 1
SPLIT_DEG_ZODIACAL = 8
STARFILE = 'sefstars.txt'
STARFILE_OLD = 'fixstars.cat'
SUN = 0
TIDAL_26 = -26.0
TIDAL_AUTOMATIC = 999999
TIDAL_DE200 = -23.8946
TIDAL_DE403 = -25.58
TIDAL_DE404 = -25.58
TIDAL_DE405 = -25.826
TIDAL_DE406 = -25.826
TIDAL_DE421 = -25.85
TIDAL_DE422 = -25.85
TIDAL_DE430 = -25.82
TIDAL_DE431 = -25.8
TIDAL_DE441 = -25.936
TIDAL_DEFAULT = -25.8
TIDAL_JPLEPH = -25.8
TIDAL_MOSEPH = -25.58
TIDAL_STEPHENSON_2016 = -25.85
TIDAL_SWIEPH = -25.8
TJD_INVALID = 99999999.0
TRUE_NODE = 11
TRUE_TO_APP = 0
URANUS = 7
VARUNA = 30000
VENUS = 3
VERTEX = 3
VESTA = 20
VULCAN = 55
VULKANUS = 46
WALDEMATH = 58
WHITE_MOON = 56
ZEUS = 42
version = '2.10.03'