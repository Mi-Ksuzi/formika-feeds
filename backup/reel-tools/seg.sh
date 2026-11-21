GRADE="eq=contrast=1.08:saturation=1.06:gamma=0.98,colortemperature=temperature=6200:mix=0.4,unsharp=5:5:0.5"
seg(){ local o=$1 f=$2 ss=$3 to=$4 dur=$5 z0=$6 z1=$7 fx=${8:-0.5} fy=${9:-0.5}; local N=$(python3 -c "print(round($dur*30))"); local SP=$(python3 -c "print(round(($to-$ss)/$dur,4))")
 local PRE="setpts=PTS/$SP,fps=30"; if python3 -c "import sys;sys.exit(0 if $SP<0.95 else 1)"; then PRE="scale=1080:1920,setpts=PTS/$SP,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1"; fi
 ffmpeg -nostdin -y -v error -ss $ss -to $to -i $f -an -vf "$PRE,tpad=stop_mode=clone:stop_duration=1,scale=2160:3840:flags=lanczos,zoompan=z='$z0+($z1-$z0)*on/$N':x='max(0,min(iw-iw/zoom,$fx*iw-iw/zoom/2))':y='max(0,min(ih-ih/zoom,$fy*ih-ih/zoom/2))':d=1:s=1080x1920:fps=30,$GRADE" -frames:v $N -c:v libx264 -preset fast -crf 17 -pix_fmt yuv420p $o.mp4; echo "file $(basename $o).mp4" >> $(dirname $o)/list.txt; }
render(){ local r=$1 D=$2 T1=$3 T2=$4 T3=$5 TE=$6 out=$7
 set -- $T1; local a1=$1 b1=$2; set -- $T2; local a2=$1 b2=$2; set -- $T3; local a3=$1 b3=$2; set -- $TE; local ae=$1 be=$2
 ffmpeg -nostdin -y -v error -i $r/v.mp4 -i $r/music.wav -loop 1 -i $r/l1.png -loop 1 -i $r/l2.png -loop 1 -i $r/l3.png -loop 1 -i $r/end.png -filter_complex "
[2]format=rgba,fade=t=in:st=$a1:d=0.35:alpha=1,fade=t=out:st=$(python3 -c "print($b1-0.3)"):d=0.3:alpha=1[o1];
[3]format=rgba,fade=t=in:st=$a2:d=0.35:alpha=1,fade=t=out:st=$(python3 -c "print($b2-0.3)"):d=0.3:alpha=1[o2];
[4]format=rgba,fade=t=in:st=$a3:d=0.35:alpha=1,fade=t=out:st=$(python3 -c "print($b3-0.3)"):d=0.3:alpha=1[o3];
[5]format=rgba,fade=t=in:st=$ae:d=0.5:alpha=1,fade=t=out:st=$(python3 -c "print($be-0.4)"):d=0.4:alpha=1[o4];
[0][o1]overlay=shortest=1[x1];[x1][o2]overlay=shortest=1[x2];[x2][o3]overlay=shortest=1[x3];[x3][o4]overlay=shortest=1,fade=t=out:st=$(python3 -c "print($D-0.35)"):d=0.35[v]" -map "[v]" -map 1:a -t $D -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -movflags +faststart $out; }
mkmusic(){ local r=$1 D=$2 seed=$3; python3 $BIN/chill.py $r/raw.wav $D $seed >/dev/null
 ffmpeg -nostdin -v error -y -i $r/raw.wav -af "aecho=0.8:0.55:70|150|260:0.3|0.2|0.12,lowpass=f=10000,atrim=0:$D,afade=t=in:d=0.3,afade=t=out:st=$(python3 -c "print($D-1.5)"):d=1.5,loudnorm=I=-32.5:TP=-9:LRA=7" -ar 48000 $r/music.wav; }
