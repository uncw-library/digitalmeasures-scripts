import os
from datetime import datetime

from rdflib import Literal
from rdflib.namespace import RDF, XSD

from globals import NS, VITRO


def add_profile_image(graph, user_id, fac_node):

    """
    If we do add a profile image node when there is no source image,
        the display will override the default profile image
        and will display an error image instead.
    So we need exit early if the user has no image.
    """

    # if not has_image(user_id):
    #     return

    """
	Maybe connect the thumbnail generator here
	Maybe do some logic renaming & moving the files to where vivo wants them
    Currently expecting jpg format for all images 
    """

    """
    If the user_id == "1234567890":
        and we make the image FileByteStream node == "1234567890999"
            with directDownloadUrl == "/file/n1234567890999/ImageName.jpg"
        and the background image FileByteStream node == "1234567890333"
            with directDownloadUrl == "/file/n1234567890333/thumbnail_ImageName.jpg"
    then:
	Vivo wants main image in:
		/usr/local/VIVO/home/uploads/file_storage_root/a~n/123/456/789/099/9/ImageName.jpg
		which can be accessed at http://localhost:8080/file/n1234567890999/ImageName.jpg
	and thumbnail image in:
		/usr/local/VIVO/home/uploads/file_storage_root/a~n/123/456/789/033/3/thumbnail_ImageName.jpg
		which can be accessed at http://localhost:8080/file/n1234567890333/thumbnail_ImageName.jpg
	"""

    file_id = f"n{user_id}"  # n7074
    filepath_id = f"n{user_id}999"  # n4443
    thumbnail_id = f"n{user_id}666"  # n637
    thumbnail_filepath_id = f"n{user_id}333"  # n5645

    file_node = NS[file_id]
    filepath_node = NS[filepath_id]
    thumbnail_node = NS[thumbnail_id]
    thumbnail_filepath_node = NS[thumbnail_filepath_node]

    now = datetime.now().isoformat(timespec="seconds")

    graph.add((fac_node, VITRO.mainImage, file_node))

    graph.add((file_node, RDF.type, VITRO.File))
    graph.add((file_node, VITRO.filename, Literal(f"{user_id}.jpg")))
    graph.add((file_node, VITRO.mimeType, Literal("image/jpeg")))
    graph.add((file_node, VITRO.modTime, Literal(now, datatype=XSD.dateTime)))
    graph.add((file_node, VITRO.downloadLocation, filepath_node))
    graph.add((file_node, VITRO.thumbnailImage, thumbnail_node))

    graph.add((filepath_node, RDF.type, VITRO.FileByteStream))
    graph.add((filepath_node, VITRO.modTime, Literal(now, datatype=XSD.dateTime)))
    graph.add(
        (
            filepath_node,
            VITRO.directDownloadUrl,
            Literal(f"/file/{filepath_id}/{user_id}.jpg"),
        )
    )

    graph.add((thumbnail_node, RDF.type, VITRO.File))
    graph.add((thumbnail_node, VITRO.filename, Literal(f"{user_id}.jpg")))
    graph.add((thumbnail_node, VITRO.mimeType, Literal("image/jpeg")))
    graph.add((thumbnail_node, VITRO.modTime, Literal(now, datatype=XSD.dateTime)))
    graph.add((thumbnail_node, VITRO.downloadLocation, thumbnail_filepath_node))

    graph.add((thumbnail_filepath_node, RDF.type, VITRO.FileByteStream))
    graph.add(
        (thumbnail_filepath_node, VITRO.modTime, Literal(now, datatype=XSD.dateTime))
    )
    graph.add(
        (
            thumbnail_filepath_node,
            VITRO.directDownloadUrl,
            Literal(f"/file/{thumbnail_filepath_id}/{user_id}.jpg"),
        )
    )


def has_image(user_id):
    expected_imagepath = os.path.join(
        "output", "profile_images", os.path.join(user_id, ".jpg")
    )
    if not os.path.isfile(expected_imagepath):
        return False
    return True
