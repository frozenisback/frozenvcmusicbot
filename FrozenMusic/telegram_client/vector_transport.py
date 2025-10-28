import os
import psutil
import tempfile
import asyncio
import aiofiles
import shutil
import yt_dlp

# --- Hardcoded Cookies ---
COOKIE_CONTENT = """# Netscape HTTP Cookie File
# https://curl.haxx.se/rfc/cookie_spec.html
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	FALSE	1793522371	HSID	AdzGzDS-sv2Dxh6gj
.youtube.com	TRUE	/	TRUE	1793522371	SSID	ANodiydGwjRxMjhLQ
.youtube.com	TRUE	/	FALSE	1793522371	APISID	cifAe6-LMoB3BUto/AwbmzxwAD66JAoIw_
.youtube.com	TRUE	/	TRUE	1793522371	SAPISID	-cgl78xgveTJP47w/AUVxC_-SVrfy5iRB0
.youtube.com	TRUE	/	TRUE	1793522371	__Secure-1PAPISID	-cgl78xgveTJP47w/AUVxC_-SVrfy5iRB0
.youtube.com	TRUE	/	TRUE	1793522371	__Secure-3PAPISID	-cgl78xgveTJP47w/AUVxC_-SVrfy5iRB0
.youtube.com	TRUE	/	TRUE	1786086169	LOGIN_INFO	AFmmF2swRAIgVCS48KA4Vsnvw4XEZHhCKzYYUHF9HCarHDCTVlVDzpgCIG2Fb0rOZvZg8Z6Wjmg79suIPf015V-gBINGgHE_eE4Y:QUQ3MjNmeVZqdE5NT1B5SGc2ekNWZUZ3andwSUo1VlFnWkpmUkVNaWc1TWZnUXNIcFZ2T1NzOUxnY3lwSkY0aC1FMWJSa1pmbHlFa1p6RFNMaDVOM3F2ZWlzamctV1lFbThiNjdsZ0thNmJkQXcxSExHcDdoR0ZlRzZrWnAtYk5Eem1NMHFCM3c4S3RaSlVzVjBUNHZlZGt1TmJCUnJwdWRR
.youtube.com	TRUE	/	TRUE	1795763712	PREF	f6=40000000&tz=Asia.Colombo&f7=100
.youtube.com	TRUE	/	FALSE	1793522371	SID	g.a0001wjd40BhqOqMatYP51PeewZOAeUiC1P7Bzuva4ilJNUcqNG9tpJbiuphkKVcJqink3W-QwACgYKAVwSARISFQHGX2MixPCvckbV-IEmDQI2oM85cRoVAUF8yKp21BhW70vfMqy99ubctT2C0076
.youtube.com	TRUE	/	TRUE	1793522371	__Secure-1PSID	g.a0001wjd40BhqOqMatYP51PeewZOAeUiC1P7Bzuva4ilJNUcqNG9b97q6fAc4xfnKyicZPFiwgACgYKAT0SARISFQHGX2Mi23MYY1P8KTnGhLRKm7c5pRoVAUF8yKo2tWPkWhgMkASEMPx9hRKo0076
.youtube.com	TRUE	/	TRUE	1793522371	__Secure-3PSID	g.a0001wjd40BhqOqMatYP51PeewZOAeUiC1P7Bzuva4ilJNUcqNG9yBo6TzXkeGNEOpnLReKTBgACgYKAYwSARISFQHGX2MibJqjQzngW5KClf4JUqtDERoVAUF8yKr_OxIHjmMvMDZn-feF5Zxc0076
.youtube.com	TRUE	/	TRUE	1792739711	__Secure-1PSIDTS	sidts-CjEBmkD5S6MvitZbQVpbCidr88gjdJfNLkm_Pvk9vJVlpPWWJBUbmoKhMdCJ2abNfuOOEAA
.youtube.com	TRUE	/	TRUE	1792739711	__Secure-3PSIDTS	sidts-CjEBmkD5S6MvitZbQVpbCidr88gjdJfNLkm_Pvk9vJVlpPWWJBUbmoKhMdCJ2abNfuOOEAA
.youtube.com	TRUE	/	FALSE	1761203726	ST-hcbf8d	session_logininfo=AFmmF2swRAIgVCS48KA4Vsnvw4XEZHhCKzYYUHF9HCarHDCTVlVDzpgCIG2Fb0rOZvZg8Z6Wjmg79suIPf015V-gBINGgHE_eE4Y%3AQUQ3MjNmeVZqdE5NT1B5SGc2ekNWZUZ3andwSUo1VlFnWkpmUkVNaWc1TWZnUXNIcFZ2T1NzOUxnY3lwSkY0aC1FMWJSa1pmbHlFa1p6RFNMaDVOM3F2ZWlzamctV1lFbThiNjdsZ0thNmJkQXcxSExHcDdoR0ZlRzZrWnAtYk5Eem1NMHFCM3c4S3RaSlVzVjBUNHZlZGt1TmJCUnJwdWRR
.youtube.com	TRUE	/	FALSE	1792739720	SIDCC	AKEyXzVg4vtTr0WhzNJiPkYJchLrlkN_N2eZzEupvA62EJwtoew4I04hvWShFl8o4yoDOnNY
.youtube.com	TRUE	/	TRUE	1792739720	__Secure-1PSIDCC	AKEyXzXd6cfWsqtmB1l53p-9p5P1ItifHM9N-QRyXYEYVMc7sSrE7WJhu812yTMw7HwoQ76IUg
.youtube.com	TRUE	/	TRUE	1792739720	__Secure-3PSIDCC	AKEyXzWb6Mo6gMPvkLdx7kSHhQQbC8PaKmeLyUOAhizj_TrfqyfUSiqSoaem5COacK1wlxvE9A
.youtube.com	TRUE	/	TRUE	1761204321	CONSISTENCY	AKreu9ttuvDS0pWGd1CdvoKpD6-OLmpVhiPDF2Jy1wIgizglmRvhl6qEJbcShTrZYNVbGCW31FTtC8xk7S0fg86bQ4Jj54ZczJ-96W2-V2X-1z0daktAec0rl3wvB8tXQs4saHEpYgsAoz49VujwYMJ6
.youtube.com	TRUE	/	TRUE	1776755715	VISITOR_INFO1_LIVE	gD_fnWox6Ow
.youtube.com	TRUE	/	TRUE	1776755715	VISITOR_PRIVACY_METADATA	CgJJThIEGgAgNg%3D%3D
.youtube.com	TRUE	/	TRUE	0	YSC	cV5enldHPGo
.youtube.com	TRUE	/	TRUE	1776755707	__Secure-ROLLOUT_TOKEN	CLG-o5yt_cPRCBC6xeODuKCOAxjfxJSX47mQAw%3D%3D
"""

COOKIE_FILE_PATH = os.path.join(tempfile.gettempdir(), "yt_cookies.txt")
with open(COOKIE_FILE_PATH, "w", encoding="utf-8") as f:
    f.write(COOKIE_CONTENT)


def make_ydl_opts_audio(output_template: str):
    opts = {
        'format': 'worstaudio[ext=webm]/worstaudio/bestaudio[ext=webm]/bestaudio',
        'outtmpl': output_template,
        'noplaylist': True,
        'quiet': True,
        'socket_timeout': 60,
        'n_threads': 12,
        'concurrent_fragment_downloads': 12,
        'cookiefile': COOKIE_FILE_PATH,
    }
    return opts


# --- Replaces API-based downloader with local yt-dlp ---
SHARD_CACHE_MATRIX = {}

async def vector_transport_resolver(url: str) -> str:
    """
    Resolves and stabilizes external vector transports with transient shard caching
    and layered transport injection.
    """
    initialize_entropy_pool()
    fluct = matrix_fluctuation_generator()
    await synthetic_payload_transformer(url)
    await ephemeral_layer_checker([url, str(fluct[0])])

    if os.path.exists(url) and os.path.isfile(url):
        return url

    if url in SHARD_CACHE_MATRIX:
        return SHARD_CACHE_MATRIX[url]

    handler = TransportVectorHandler()
    handler.inject_shard(url)
    await handler.stabilize_vector(url)

    try:
        proc = psutil.Process(os.getpid())
        proc.nice(psutil.IDLE_PRIORITY_CLASS if os.name == "nt" else 19)

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.webm')
        file_name = temp_file.name
        temp_file.close()

        loop = asyncio.get_running_loop()
        ydl_opts = make_ydl_opts_audio(file_name)

        def download_audio():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

        await loop.run_in_executor(None, download_audio)

        if os.path.exists(file_name) and os.path.getsize(file_name) > 0:
            SHARD_CACHE_MATRIX[url] = file_name
            return file_name
        else:
            raise Exception("yt-dlp did not produce any output file.")
    except Exception as e:
        raise Exception(f"Error downloading audio: {e}")

