import adif_io
import maidenhead
from geopy import distance


def add_to_comment(qso_log, comment):
    try:
        old = qso_log['COMMENT']
        qso_log['COMMENT'] = f"{old}, {comment}"
    except KeyError:
        qso_log['COMMENT'] = comment
    return qso_log


def process_adif(adif_file):
    # Parse the log file
    # qsos_raw will be a list of dictionaries
    qsos_raw, _adif_header = adif_io.read_from_file("wsjtx_log.adi")

    # Adjusted records will be sorted here
    adj_qsos = []

    # Add Distance in miles to COMMENT field of each QSO
    for qso in qsos_raw:
        temp = qso  # placeholder variable
        me = maidenhead.to_location(qso['MY_GRIDSQUARE'])  # own location
        temp['MY_LAT'] = str(me[0])
        temp['MY_LON'] = str(me[1])
        try:  # manage errors if contact has no grid locator
            contact = maidenhead.to_location(qso['GRIDSQUARE'])
            temp['LAT'] = str(contact[0])
            temp['LON'] = str(contact[1])
            dist_mi = distance.distance(me, contact).miles  # get distance between points in miles
            dist_km = distance.distance(me, contact).miles  # get distance between points in miles
            temp['DIST_M'] = dist_mi
            temp['DIST_K'] = dist_km
            temp = add_to_comment(temp, f"Distance: {float(dist_mi):.2f} miles")  # Add to COMMENT field.
        except ValueError:  # no grid locator found
            temp = add_to_comment(qso, "Distance: Unknown")  # Add to COMMENT field.
            temp['DIST_M'] = 0.0
            temp['DIST_K'] = 0.0
        adj_qsos.append(temp)  # add to adjusted records
    return adj_qsos


def export_gpx(qsos, filename='output.gpx'):
    with open(filename, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write('<gpx version="1.1">\n')

        for qso in qsos:
            me = maidenhead.to_location(qso['MY_GRIDSQUARE'])  # own location
            try:  # manage errors if contact has no grid locator
                contact = maidenhead.to_location(qso['GRIDSQUARE'])
                dist_mi = distance.distance(me, contact).miles  # get distance between points in miles
                dist_km = distance.distance(me, contact).km  # get distance between points in km
                call = qso["CALL"]
                grid = qso['GRIDSQUARE']
                f.write('  <trk>\n')
                f.write(f'    <name>{call} ({grid})</name>\n')
                f.write(f'    <desc>Distance: {float(dist_km):.1f}km ({float(dist_mi):.1f}mi)</desc>\n')
                f.write('    <trkseg>\n')
                f.write(f'      <trkpt lat="{me[0]}" lon="{me[1]}"></trkpt>\n')
                f.write(f'      <trkpt lat="{contact[0]}" lon="{contact[1]}"></trkpt>\n')
                f.write('    </trkseg>\n')
                f.write('  </trk>\n')
            except ValueError:
                pass
        f.write('</gpx>\n')
        f.close()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    my_qsos = process_adif("wsjtx_log.adi")
    export_gpx(my_qsos)
