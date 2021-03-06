% Alberto Cereser, September 2017
% DTU Fysik, alcer@fysik.dtu.dk

% This script converts the reconstructed volume returned by recon3d.py in a
% vtk file, that can be visualized using ParaView. The volume is also saved as a
% .mat. To select the sample volume, a completeness threshold is used

close all; clear;

% To be part of the sample volume, a voxel mush have completeness value greater
% than compl_thr
compl_thr = 0.5;

addpath('/npy_matlab_master/');
% Read reconstructed volume. Format: X, Y, Z, param. Parameters: gamma, mu,
% completeness
V = readNPY('/u/data/alcer/DFXRM_rec/Rec_test_2/grain_ang.npy');

% Volume selected using completeness
V_th = zeros(size(V,1), size(V,2), size(V,3));
% Volume with angular values
V_th_mos = zeros(size(V,1), size(V,2), size(V,3), 3);

for ii =1:size(V,1)
    for jj = 1:size(V,2)
        for kk = 1:size(V,3)
            % The minimum completeness value for a voxel
            % to be part of the volume is
            if V(ii,jj,kk,3) > compl_thr
                V_th(ii,jj,kk) = V(ii,jj,kk,3);
                V_th_mos(ii,jj,kk,:) = V(ii,jj,kk,:);
            end
        end
    end
end

% Save the selected region
save('V_mos_recon3d.mat', 'V_th_mos');

% Rescale, se we can compare with the reconstruction from ART+TV
V_resc = zeros((size(V,1) * 3) -3, (size(V,2) * 3) -3, (size(V,3) * 3) - 3);
for jj = 1:(size(V,3) - 1)
    Layer = squeeze(V_th(1:100,1:100,jj));
    Layer_resc = imresize(Layer, 3);
    V_resc(:,:,jj) = Layer_resc(:,:);
end

% Save calculated volumes
savevtk(V_th, '/u/data/alcer/DFXRM_rec/Rec_test_2/V_th.vtk');
