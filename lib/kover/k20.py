"""
Kodi wrappers for K20 with K19 API.
"""

from typing import Union, Any, Tuple, List, Dict, Callable
from wrapt.wrappers import ObjectProxy

import xbmc
import xbmcgui
from xbmcgui import ListItem as xbmcgui_ListItem
from xbmc import VideoStreamDetail, AudioStreamDetail, SubtitleStreamDetail
from xbmc import InfoTagVideo, InfoTagMusic, InfoTagPicture, InfoTagGame, InfoTagRadioRDS
from xbmc import Actor


InfoTag = Union[InfoTagVideo, InfoTagMusic, InfoTagPicture, InfoTagGame, InfoTagRadioRDS]


class InfoTagMusicWrapper(ObjectProxy):
    """
    Wrapper for InfoTagVideo, implements K19 API.
    """

    def getGenre(self) -> str:
        """
        Returns the genre name from music tag as string if present.

        Returns
        -------
        str
            Genre name
        """
        lst = self.getGenres()
        return lst[0] if lst else ''

    def getLastPlayed(self) -> str:
        """
        Returns last played time as string from music info tag.

        Returns
        -------
        str
            Last played date / time on tag
        """
        return self.getLastPlayedAsW3C()


class InfoTagVideoWrapper(ObjectProxy):
    """
    Wrapper for InfoTagVideo, implements K19 API.
    """

    def getGenre(self) -> str:
        """
        Returns the genre name from music tag as string if present.

        Returns
        -------
        str
            Genre name
        """
        genres = self.getGenres()
        if genres:
            return genres[0]

    def getLastPlayed(self) -> str:
        """
        Returns last played time as string from music info tag.

        Returns
        -------
        str
            Last played date / time on tag
        """
        # TODO: reformat date 'YYYY-MM-DDThh:mm:ssTZD' to local.
        return self.getLastPlayedAsW3C()

    def getCast(self) -> str:
        """
        To get the cast of the video when available.

        Returns
        -------
        str
            Video casts, one per line
        """
        return '\n'.join(f'{a.getName()}: {a.getRole()}' for a in self.getActors())

    def getDirector(self) -> str:
        """
        Get film director who has made the film (if present).

        Returns
        -------
        str
            Film director name.
        """
        lst = self.getDirectors()
        return lst[0] if lst else ''

    def getFirstAired(self) -> str:
        """
        Returns first aired date as string from info tag.

        Returns
        -------
        str
            First aired date
        """
        # TODO: reformat date 'YYYY-MM-DD' to local.
        return self.getFirstAiredAsW3C()

    def getPremiered(self) -> str:
        """
        To get premiered date of the video, if available.

        Returns
        -------
        str
            Date
        """
        # TODO: reformat date 'YYYY-MM-DD' to local.
        return self.getPremieredAsW3C()

    def getVotes(self) -> str:
        """
        Get the video votes if available from video info tag.

        Returns
        -------
        str
            Votes
        """
        return str(self.getVotesAsInt())

    def getWritingCredits(self) -> str:
        """
        Get the writing credits if present from video info tag.

        Returns
        -------
        str
            Writing credits
        """
        lst = self.getWriters()
        return lst[0] if lst else ''


def set_cast_and_role(tag: InfoTag, actors: List[Tuple[str, str]]) -> None:
    """Helper. Set actors form 'CastAndRole' info label."""
    tag.setCast([Actor(*a) for a in actors])


def set_cast(tag: InfoTag, actors: List[Union[Dict[str, Any], Tuple[str, str]]]) -> None:
    """Helper. Set actors form 'Cast' info label."""
    if actors:
        if isinstance(actors[0], dict):
            tag.setCast([Actor(**a) for a in actors])
        else:
            tag.setCast([Actor(*a) for a in actors])


def set_imdb_number(tag: InfoTag, imdb: str) -> None:
    """Helper. Set imdb id/number."""
    tag.setUniqueID(str(imdb), 'imdb')


def set_exif_resolution(tag: InfoTag, res: str) -> None:
    """Helper. Set picture resolution (W,H)."""
    w, h = res.split(',')
    tag.setResolution(int(w), int(h))


def one_or_more(tag: InfoTag, value: Union[Any, List[Any]]) -> List[Any]:
    """Helper. Returns a list of value event if a single element is provided."""
    return value if isinstance(value, (tuple, list)) else [value]
    # return [value] if isinstance(value, (str, Mapping)) or not isinstance(value, Sequence) else value


def int_or_none(tag: InfoTag, value: Union[int, str]) -> int:
    """Helper. Convert to integer or return -1."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        value = value.replace(',', '')
        if '.' in value:
            return int(float(value) + .5)
    return int(value) if value else -1


def float_or_none(tag: InfoTag, value: Union[float, int, str]) -> float:
    """Helper. Convert to float or return -1."""
    if isinstance(value, (int, float)):
        return value
    # TODO: regex for same strage like: 1,234.45 ?
    if isinstance(value, str):
        if value.count(',') == 1 and not value.count('.'):
            value = value.replace(',', '.')
    return float(value) if value else -1


#: Keys for `ListItem.setInfo(infoLabels)`. Values could be callable or InfoTag setter method name.
info_label_keys: Dict[str, List[Union[str, Callable]]] = {
    # video
    'aired': ['setFirstAired'],
    'album': ['setAlbum'],
    'artist': ['setArtists'],
    'castandrole': [set_cast_and_role],
    'cast': [set_cast],
    'code': ['setProductionCode'],
    'country': [one_or_more, 'setCountries'],
    'credits': [one_or_more, 'setWriters'],
    'dateadded': ['setDateAdded'],
    'dbid': [int_or_none, 'setDbId'],
    'director': [one_or_more, 'setDirectors'],
    'duration': [int_or_none, 'setDuration'],
    'episodeguide': ['setEpisodeGuide'],
    'episode': [int_or_none, 'setEpisode'],
    'genre': [one_or_more, 'setGenres'],
    'imdbnumber': [set_imdb_number],
    'lastplaye': ['setLastPlayed'],
    'mediatype': ['setMediaType'],
    'mpaa': ['setMpaa'],
    'originaltitle': ['setOriginalTitle'],
    'path': ['setPath'],
    'playcount': [int_or_none, 'setPlaycount'],
    'plotoutline': ['setPlotOutline'],
    'plot': ['setPlot'],
    'premiered': ['setPremiered'],
    'rating': [float_or_none, 'setRating'],
    'season': [int_or_none, 'setSeason'],
    'setid': [int_or_none, 'setSetId'],
    'setoverview': ['setSetOverview'],
    'set': ['setSet'],
    'showlink': [one_or_more, 'setShowLinks'],
    'sortepisode': [int_or_none, 'setSortEpisode'],
    'sortseason': [int_or_none, 'setSortSeason'],
    'sorttitle': ['setSortTitle'],
    'status': ['setTvShowStatus'],
    'studio': [one_or_more, 'setStudios'],
    'tagline': ['setTagLine'],
    'tag': [one_or_more, 'setTags'],
    'title': ['setTitle'],
    'top250': [int_or_none, 'setTop250'],
    'tracknumber': [int_or_none, 'setTrackNumber'],
    'trailer': ['setTrailer'],
    'tvshowtitle': ['setTvShowTitle'],
    'userrating': [int_or_none, 'setUserRating'],
    'votes': [int_or_none, 'setVotes'],
    'watched': [int_or_none, 'setPlaycount'],
    'writer': [one_or_more, 'setWriters'],
    'year': [int_or_none, 'setYear'],

    # music (if not defined above already)
    'comment': ['setComment'],
    'discnumber': ['setDisc'],
    'listeners': [int_or_none, 'setListeners'],
    'lyrics': ['setLyrics'],
    'musicbrainzalbumartistid': ['setMusicBrainzAlbumArtistID'],
    'musicbrainzalbumid': ['setMusicBrainzAlbumID'],
    'musicbrainzartistid': ['setMusicBrainzArtistID'],
    'musicbrainztrackid': ['setMusicBrainzTrackID'],

    # picture (if not defined above already)
    'exif:resolution': [set_exif_resolution],
    'exif:exiftime': ['setDateTimeTaken'],

    # game (if not defined above already)
    'developer': ['setDeveloper'],
    'gameclient': ['setGameClient'],
    'genres': ['setGenres'],
    'overview': ['setOverview'],
    'platform': ['setPlatform'],
    'publisher': ['setPublisher'],
}


class ListItem(xbmcgui_ListItem):
    """
    xbmcgui.ListItem with K19 API.
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
            self._self_videoInfoTag = InfoTagVideoWrapper(super().getVideoInfoTag())
        return self._self_videoInfoTag

    def getMusicInfoTag(self):
        """Returns the MusicInfoTag for this item."""
        if self._self_musicInfoTag is None:
            self._self_musicInfoTag = InfoTagMusicWrapper(super().getMusicInfoTag())
        return self._self_musicInfoTag

    def addAvailableArtwork(self,
                            url: str,
                            art_type: str,
                            preview: str = '',
                            referrer: str = '',
                            cache: str = '',
                            post: bool = False,
                            isgz: bool = False,
                            season: str = '',
                            ) -> None:
        """
        Add an image to available artworks (needed for video scrapers)

        Parameters
        ----------
        url : str
            image path url
        art_type : str
            image type
        preview : str
            image preview path url
        referrer : str
            referrer url
        cache : str
            filename in cache
        post : bool
            use post to retrieve the image, default false
        isgz : bool
            use gzip to retrieve the image, default false
        season : str
            number of season in case of season thumb
        """
        season = int(season) if season else -1
        return super().getVideoInfoTag().addAvailableArtwork(url, art_type=art_type, preview=preview,
                                                             referrer=referrer, cache=cache, post=post,
                                                             isgz=isgz, season=season)

    def addSeason(self, number, name: str = '') -> None:
        """
        Add a season with name to a listitem. It needs at least the season number

        Parameters
        ----------
        number : int
            the number of the season.
        name : str
            the name of the season. Default "".
        """
        return super().getVideoInfoTag().addSeason(number, name)

    def addStreamInfo(self, type: str, values: Dict[str, Any]) -> None:
        """
        Add a season with name to a listitem. It needs at least the season number

        Parameters
        ----------
        type : str
             type of stream(video/audio/subtitle)
        values : dict of str, any
            pairs of { label: value }
        """
        vtag = super().getVideoInfoTag()
        if type == 'video':
            vtag.addVideoStream(VideoStreamDetail(**values))
        elif type == 'audio':
            vtag.addAudioStream(AudioStreamDetail(**values))
        elif type == 'subtitle':
            vtag.addSubtitleStream(SubtitleStreamDetail(**values))
        else:
            raise ValueError(f'ListItem.addStreamInfo type must be one of video, audio, subtitle, not {type!r}')

    def getRating(self, key: str) -> float:
        """
        Returns a listitem rating as a float.

        Parameters
        ----------
        key : str
            rating type, one of imdb/tvdb/tmdb/anidb or another

        Returns
        -------
        float
            the listitem rating
        """
        return super().getVideoInfoTag().getRating(key)

    def setRating(self, type: str, rating: float, votes: int = 0, defaultt: bool = False) -> None:
        """
        Sets a listitem's rating. It needs at least type and rating param

        Parameters
        ----------
        type : str
            the type of the rating, any string. One of imdb/tvdb/tmdb/anidb or another.
        rating : float
            the value of the rating.
        votes : int
            the number of votes. Default 0.
        defaultt : bool
            is the default rating?. Default False.
        """
        # Paramters order is changed in K20
        return super().getVideoInfoTag().setRating(rating, votes, type, defaultt)

    def getUniqueID(self, key: str) -> str:
        """
        Returns a listitem uniqueID as a string, similar to an infolabel.

        Parameters
        ----------
        key : str
            uniqueID name, one of imdb/tvdb/tmdb/anidb or another

        Returns
        -------
        str
            the listitem unique ID name
        """
        return super().getVideoInfoTag().getUniqueID(key)

    def setUniqueIDs(values: Dict[str, str], defaultrating: str = '') -> None:
        """
        Returns a listitem uniqueID as a string, similar to an infolabel.

        Parameters
        ----------
        values : dict of str, st
            pairs of { label: value }, labe is a uniqueID name, one of imdb/tvdb/tmdb/anidb or another
        defaultrating : str
            the name of default rating
        """
        return super().getVideoInfoTag().setUniqueIDs(values, defaultrating or '')

    def getVotes(self, key: str) -> int:
        """
        Returns a listitem rating as a float.

        Parameters
        ----------
        key : str
            rating type, one of imdb/tvdb/tmdb/anidb or another

        Returns
        -------
        int
            the listitem votes
        """
        return super().getVideoInfoTag().getRating(key)

    def setCast(self, actors: List[Dict[str, Any]]) -> None:
        """
        Set cast including thumbnails.

        Parameters
        ----------
        actors : list of dict of str, any
            list of actor data (name: str, role: str, thumbnail: str, order: int)
        """
        actors = [Actor(**a) for a in actors]
        return super().getVideoInfoTag().setCast(actors)

    def setInfo(self, type: str, infoLabels: Dict[str, Any]) -> None:
        """
        Sets the listitem's infoLabels.

        Parameters
        ----------
        type : str
            type of info labels, one of video/music/pictures/game
        infoLabels : dict of str, any
            pairs of { label: value }

        See: https://alwinesch.github.io/group__python__xbmcgui__listitem.html#ga0f1e91e1d5aa61d8dd0eac90e8edbf18
        """

        type = type.capitalize()
        tag: InfoTag = getattr(super(), f'get{type}InfoTag')()

        labels = {}
        for key, value in infoLabels.items():
            operations = info_label_keys.get(key.lower())
            if operations is None:
                labels[key] = value
            else:
                for op in operations:
                    try:
                        if isinstance(op, str):
                            value = getattr(tag, op)(value)
                        else:
                            value = op(tag, value)
                    except Exception as exc:
                        import sys
                        print(f'Incorrect K20 setInfo: {key} → {op!r}: {exc!r}', file=sys.stderr, end='')
                        raise
        if labels:
            super().setInfo(type, labels)

    def getProperty(self, key: str) -> Any:
        """
        Returns a listitem property as a string, similar to an infolabel.

        Parameters
        ----------
        key : str
            property name

        Key is NOT case sensitive.
        """
        lower_key: str = key.lower()
        if lower_key == 'resumetime':
            return super().getVideoInfoTag().getResumeTime()
        if lower_key == 'totaltime':
            return super().getVideoInfoTag().getResumeTimeTotal()
        return super().getProperty(key)

    def _set_resume_point(self) -> None:
        """Helper. Set resume point via K20 API with property values."""
        if self._self_resume_time is not None:
            if self._self_resume_total_time is None:
                return super().getVideoInfoTag().setResumePoint(self._self_resume_total_time)
            else:
                return super().getVideoInfoTag().setResumePoint(self._self_resume_total_time,
                                                                self._self_resume_total_time)

    def setProperty(self, key: str, value: Any) -> None:
        """
        Sets a listitem property, similar to an infolabel.

        Parameters
        ----------
        key : str
            property name
        value : str or float
            value of the property

        Key is NOT case sensitive.
        """
        lower_key: str = key.lower()
        if lower_key == 'resumetime':
            self._self_resume_time = value
            return self._set_resume_point()
        if lower_key == 'totaltime':
            self._self_resume_total_time = value
            return self._set_resume_point()
        super().setProperty(key, value)

    def setProperties(self, values: Dict[str, Any]) -> None:
        """
        Sets multiple properties for listitem's

        Parameters
        ----------
        values : dict of str, str or float
            pairs of { label: value }

        Key is NOT case sensitive.
        """
        vals: Dict[str, Any] = {}
        resume_point: bool = False
        for key, value in values.items():
            lower_key: str = key.lower()
            if lower_key == 'resumetime':
                self._self_resume_time = value
                resume_point = True
            elif lower_key == 'totaltime':
                self._self_resume_total_time = value
                resume_point = True
            else:
                vals[key] = value
        if vals:
            super().setProperties(vals)
        if resume_point:
            self._set_resume_point()


def _patch():
    """
    Monkey patching.
    """
    if not getattr(xbmc, '_patched_by_kover', None):
        xbmcgui.ListItem = ListItem
        xbmc._patched_by_kover = True


__all__ = ('_patch', 'ListItem')
