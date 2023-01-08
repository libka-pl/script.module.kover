"""
Kodi wrappers for K19 with K20 API.
"""

from typing import Union, Any, Callable, Tuple, List, Dict
from collections.abc import Sequence
from dataclasses import dataclass, asdict

from wrapt.wrappers import ObjectProxy

import xbmc
import xbmcgui

from xbmc import InfoTagVideo as xbmc_InfoTagVideo
from xbmc import InfoTagMusic as xbmc_InfoTagMusic
from xbmcgui import ListItem as xbmcgui_ListItem


def kodi_list(val: Union[Any, List[Any]]) -> List[Any]:
    if not val:
        return []
    if isinstance(val, str) or not isinstance(val, Sequence):
        return [val]
    return val


class GetSetMixin:
    """Define getXxx() and setXxx() methods."""

    def __getattr__(self, key: str) -> Callable:
        if key.startswith('get') and key[3:4].isupper():
            def getter() -> Any:
                return getattr(self, key)
            key = f'{key[3].lower()}{key[4:]}'
            return getter
        if key.startswith('set'):
            def setter(value: Any) -> None:
                setattr(self, key, value)
            key = f'{key[3].lower()}{key[4:]}'
            return setter
        raise AttributeError(key)


@dataclass
class Actor(GetSetMixin):
    """
    Represents a single actor in the cast of a video item wrapped by InfoTagVideo.
    """
    #: Name of the actor.
    name: str = ''
    #: Role of the actor in the specific video item.
    role: str = ''
    #: Order of the actor in the cast of the specific video item.
    order: int = -1
    #: Path / URL to the thumbnail of the actor.
    thumbnail: str = ''


@dataclass
class VideoStreamDetail(GetSetMixin):
    """
    Represents a single selectable video stream for a video item wrapped by InfoTagVideo.
    """
    #: Width of the video stream in pixel.
    width: int = 0
    #: Height of the video stream in pixel.
    height: int = 0
    #: Aspect ratio of the video stream
    aspect: float = 0.0
    #: Duration of the video stream in seconds.
    duration: int = 0
    #: Codec of the video stream.
    codec: str = ''
    #: Stereo mode of the video stream.
    stereoMode: str = ''
    #: Language of the video stream.
    language: str = ''
    #: (hidden argument)
    hdrType: str = ''


@dataclass
class AudioStreamDetail(GetSetMixin):
    """
    Represents a single selectable audio stream for a video item wrapped by InfoTagVideo.
    """
    #: Number of channels in the audio stream.
    channels: int = -1
    #: Codec of the audio stream.
    codec: str = ''
    #: Language of the video stream.
    language: str = ''


@dataclass
class SubtitleStreamDetail(GetSetMixin):
    """
    Subtitle stream details class used in combination with InfoTagVideo.
    """
    #: Language of the video stream.
    language: str = ''


class InfoTagWrapper(ObjectProxy):
    """
    Access and / or modify the common (video/music/picture/game) metadata of a ListItem.
    """

    _METHODS = {
    }

    def __init__(self, info_tag: Union[xbmc_InfoTagVideo, xbmc_InfoTagMusic], *,
                 list_item: 'ListItem', list_item_self_sync: bool = True):
        super().__init__(info_tag)
        #: ListItem - the owner.
        self._self_list_item: ListItem = list_item
        #: True if every set is synced, ListItem.setInfo() is called
        self._self_sync: bool = list_item_self_sync and self._self_list_item is not None
        #: ListItem infoLabels data.
        self._self_data: Dict[str, Any] = {}  # if list_item is None else list_item._self_data

    def __getattr__(self, key):
        """
        Generic getter / setter.
        """
        key = self._METHODS.get(key, key)
        func = getattr(self._self_list_item, key, None)
        if func is not None:
            return func
        if key.startswith('set') and key[3:4].isupper():
            def setter(value):
                self._self_data[key] = value
                if self._self_sync:
                    self._self_list_item.setInfo(self._type, {key: value})
            key = key[3:].lower()
            return setter
        raise AttributeError(key)

    def getDbId(self) -> int:
        """
        Get identification number of tag in database.
        """
        return self._self_data.get('dbid', '')

    def getGenres(self) -> List[str]:
        """
        Returns the genre name from music tag as string if present.
        """
        return kodi_list(self.getGenre())

    def getYear(self) -> int:
        """
        Returns the year of music as integer from info tag.
        """
        return self._self_data.get("year", 0)

    def getLastPlayedAsW3C(self) -> str:
        """
        Returns last played time as string in W3C format (YYYY-MM-DDThh:mm:ssTZD).
        """
        # TODO: reformat date to '01.01.1601 00:00:00'
        return self.getLastPlayed()

    def setDbId(self, dbId: int, type: str):
        """
        Set the database identifier of the music item.

        Parameters
        ----------
        dbId : int
            Database identifier.
        type : str
            Media type of the item.
        """
        self._self_data['dbid'] = dbId
        if self._self_sync:
            self._self_list_item.setInfo(self._type, {'dbid': dbId})

    def setMediaType(self, mediaType: str) -> None:
        """
        Set the media type of the music item.

        Parameters
        ----------
        mediaType : str
            Media type.
        """
        self._self_data['mediatype'] = mediaType
        if self._self_sync:
            self._self_list_item.setInfo(self._type, {'mediatype': mediaType})

    def setDuration(self, duration: int) -> None:
        """
        Set the duration of the song.

        Parameters
        ----------
        duration : int
            Disc number.
        """
        self._self_data['duration'] = duration
        if self._self_sync:
            self._self_list_item.setInfo(self._type, {'duration': duration})

    def setYear(self, year: int) -> None:
        """
        Set the year of the music item.

        Parameters
        ----------
        year : int
            Year.
        """
        self._self_data['year'] = year
        if self._self_sync:
            self._self_list_item.setInfo(self._type, {'year': year})


class InfoTagVideoWrapper(InfoTagWrapper):
    """
    Access and / or modify the video metadata of a ListItem.
    """

    #: InfoTag type, used in ListItem.setInfo().
    _type: str = 'video'

    def getDirectors(self) -> List[str]:
        """
        Get a list of film directors who have made the film (if present).
        """
        return kodi_list(self._self_data.get('director', ''))

    def getWriters(self) -> List[str]:
        """
        Get the list of writers (if present) from video info tag.
        """
        val = self.getWritingCredits()
        return val.split('\n') if val else []

    def getGenres(self) -> List[str]:
        """
        Get the list of Video Genres if available.
        """
        return kodi_list(self.getGenre())

    def getVotesAsInt(self, type: str) -> int:
        """
        Get the votes of the rating (if available) as an integer.

        Parameters
        ----------
        type : str
            Some rating type values (imdb/tvdb/tmdb/anidb) or any string possible.
        """
        if self._self_list_item is None:
            return 0
        return self._self_list_item.getVotes(type)

    def getActors(self) -> List[Actor]:
        """
        Get the cast of the video if available.
        """
        # TODO: parse getCast()
        return []

    def getRating(self, type: str) -> float:
        """
        Get the video rating if present as float (double where supported).

        Parameters
        ----------
        type : str
            Some rating type values (imdb/tvdb/tmdb/anidb) or any string possible.
        """
        if self._self_list_item is None:
            return .0
        return self._self_list_item.getRating(type)

    def getLastPlayedAsW3C(self) -> str:
        """
        Get last played datetime as string in W3C format (YYYY-MM-DDThh:mm:ssTZD).
        """
        # TODO; reformat date to ... something else
        return self.getLastPlayed()

    def getPremieredAsW3C(self) -> str:
        """
        Get premiered date as string in W3C format (YYYY-MM-DD).
        """
        # TODO; reformat date?
        return self.getPremiered()

    def getFirstAiredAsW3C(self) -> str:
        """
        Get first aired date as string in W3C format (YYYY-MM-DD).
        """
        # TODO; reformat date?
        return self.getFirstAired()

    def getResumeTime(self) -> float:
        """
        Gets the resume time of the video item.
        """
        if self._self_list_item is None:
            return 0
        return self._self_list_item.getProperty('ResumeTime')

    def getResumeTimeTotal(self) -> float:
        """
        Gets the total duration stored with the resume time of the video item.
        """
        if self._self_list_item is None:
            return 0
        return self._self_list_item.getProperty('TotalTime')

    def getUniqueID(self, key: str) -> str:
        """
        Get the unique ID of the given key. A unique ID is an identifier used by a (online) video database used to identify a video in its database.

        Parameters
        ----------
        key : str
            Some default uniqueID values (imdb/tvdb/tmdb/anidb) or any string possible.
        """
        if self._self_list_item is None:
            return ''
        return self._self_list_item.getUniqueID(key)

    def setUniqueID(self, uniqueID: str, type: str = '', isDefault: bool = False) -> None:
        """
        Set the given unique ID. A unique ID is an identifier used by a (online) video database used to identify a video in its database.

        Parameters
        ----------
        uniqueID : str
            value of the unique ID.
        type : str
            type / label of the unique ID.
        isDefault : bool
            whether the given unique ID is the default unique ID.
        """
        if self._self_list_item is None:
            return ''
        return self._self_list_item.setUniqueID({type: uniqueID}, type if isDefault else '')

    def addVideoStream(self, stream: VideoStreamDetail) -> None:
        """
        Add a video stream to the video item.

        Parameters
        ----------
        stream : VideoStreamDetail
            Video stream.
        """
        if self._self_list_item is not None:
            return self._self_list_item.addStreamInfo('video', asdict(stream))

    def addAudioStream(self, stream: AudioStreamDetail) -> None:
        """
        Add a audio stream to the video item.

        Parameters
        ----------
        stream : AudioStreamDetail
            Audio stream.
        """
        if self._self_list_item is not None:
            return self._self_list_item.addStreamInfo('audio', asdict(stream))

    def addSubtitleStream(self, stream: SubtitleStreamDetail) -> None:
        """
        Add a subtitle stream to the video item.

        Parameters
        ----------
        stream : SubtitleStreamDetail
            Subtitle stream.
        """
        if self._self_list_item is not None:
            return self._self_list_item.addStreamInfo('subtitle', asdict(stream))

    def setCast(self, actors: List[Actor]) -> None:
        """
        Set the cast / actors of the video item.

        Parameters
        ----------
        actors : list of Actor
            List of cast / actors
        """
        self._self_list_item.setCast([{
            'name':      actor.name,
            'role':      actor.role,
            'thumbnail': actor.thumbnail,
            'order':     actor.order,
        } for actor in actors])

    def setResumePoint(self, time: float, totalTime: float = 0.0) -> None:
        """
        Set the resume point of the video item.

        Parameters
        ----------
        time : float
            Resume point in seconds.
        totalTime : float
            Total duration in seconds.
        """
        self._self_list_item.setProperty('ResumeTime', time)
        if totalTime:
            self._self_list_item.setProperty('TotalTime', totalTime)

    def addSeasons(self, namedSeasons: List[Tuple[int, str]]) -> None:
        """
        Add named seasons to the TV show.

        Parameters
        ----------
        namedSeasons : list of tuple of int, str
            The seasons list: [ (season, name) ].
        """
        for number, name in namedSeasons or ():
            self._self_list_item.addSeason(number, name)


class InfoTagMusicWrapper(InfoTagWrapper):
    """
    Access and / or modify the music metadata of a ListItem.
    """

    #: InfoTag type, used in ListItem.setInfo().
    _type: str = 'music'

    def setURL(self, url: str) -> None:
        """
        Set the URL of the music item.

        Parameters
        ----------
        url : str
            URL.
        """
        raise NotImplementedError('InfoTagMusic.setURL')

    def setTrack(self, track: int) -> None:
        """
        Set the track number of the song.

        Parameters
        ----------
        track : int
            Track number.
        """
        self._self_data['tracknumber'] = track
        if self._self_sync:
            self._self_list_item.setInfo(self._type, {'tracknumber': track})

    def setDisc(self, disc: int) -> None:
        """
        Set the disc number of the song.

        Parameters
        ----------
        disc : int
            Disc number.
        """
        self._self_data['discnumber'] = disc
        if self._self_sync:
            self._self_list_item.setInfo(self._type, {'discnumber': disc})


class ListItem(xbmcgui_ListItem):
    """
    xbmcgui.ListItem with K20 API.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._self_videoInfoTag = None
        self._self_musicInfoTag = None
        self._self_resume_time = None
        self._self_resume_total_time = None

    def getVideoInfoTag(self):
        """Returns the VideoInfoTag for this item."""
        if self._self_videoInfoTag is None:
            self._self_videoInfoTag = InfoTagVideoWrapper(super().getVideoInfoTag(), list_item=self)
        return self._self_videoInfoTag

    def getMusicInfoTag(self):
        """Returns the MusicInfoTag for this item."""
        if self._self_musicInfoTag is None:
            self._self_musicInfoTag = InfoTagMusicWrapper(super().getMusicInfoTag(), list_item=self)
        return self._self_musicInfoTag


def _patch():
    """
    Monkey patching.
    """
    if not getattr(xbmc, '_patched_by_kover', None):
        xbmc.Actor = Actor
        xbmc.VideoStreamDetail = VideoStreamDetail
        xbmc.AudioStreamDetail = AudioStreamDetail
        xbmc.SubtitleStreamDetail = SubtitleStreamDetail
        xbmcgui.ListItem = ListItem
        xbmc._patched_by_kover = True


__all__ = ('_patch', 'Actor', 'ListItem', 'VideoStreamDetail', 'AudioStreamDetail', 'SubtitleStreamDetail')
